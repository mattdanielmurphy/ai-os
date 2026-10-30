import ActivityKit
import AlarmKit
import AppIntents
import AVFoundation
import CoreLocation
import SwiftUI

#if targetEnvironment(simulator)
let serverHost = "127.0.0.1"
#else
let serverHost = "macbook-pro.tail491454.ts.net"
#endif
let serverBase = "ws://\(serverHost):8798/ws?stages="
let startKey = "startSession"
let pingEvery = 4.0  // s between checks that the line is alive
let voiceGain: Float = 1  // loudness boost for the bot's voice
let homeRadius: CLLocationDistance = 200  // m from saved Home that counts as at home

/// One-shot location, used only to tell whether you're at home.
@MainActor final class Place: NSObject, ObservableObject, CLLocationManagerDelegate {
    @Published var hasHome = UserDefaults.standard.object(forKey: "homeLat") != nil
    @Published var status = ""
    private let manager = CLLocationManager()
    private var waiting: [(CLLocation?) -> Void] = []

    override init() {
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyHundredMeters
        manager.requestWhenInUseAuthorization()
    }

    func locate(_ done: @escaping (CLLocation?) -> Void) { waiting.append(done); manager.requestLocation() }

    func saveHome() {
        status = "Finding you…"
        locate { [self] here in
            guard let here else { status = "Couldn't get your location. Check Settings > Morning > Location."; return }
            status = "Home saved."
            UserDefaults.standard.set(here.coordinate.latitude, forKey: "homeLat")
            UserDefaults.standard.set(here.coordinate.longitude, forKey: "homeLon")
            hasHome = true
        }
    }

    /// True at home. With no saved Home or no location, also true, since mornings start in bed.
    func atHome(_ done: @escaping (Bool) -> Void) {
        let d = UserDefaults.standard
        guard hasHome else { return done(true) }
        let home = CLLocation(latitude: d.double(forKey: "homeLat"), longitude: d.double(forKey: "homeLon"))
        locate { here in done(here.map { $0.distance(from: home) < homeRadius } ?? true) }
    }

    nonisolated func locationManager(_ m: CLLocationManager, didUpdateLocations l: [CLLocation]) {
        let last = l.last
        Task { @MainActor in self.finish(last) }
    }
    nonisolated func locationManager(_ m: CLLocationManager, didFailWithError e: Error) {
        Task { @MainActor in self.finish(nil) }
    }
    private func finish(_ l: CLLocation?) { let w = waiting; waiting = []; w.forEach { $0(l) } }
}

struct Voice: Codable, Hashable { let id: String; let name: String }

struct WakeMeta: AlarmMetadata {}

/// The alarm's Start button: opens the app and asks it to begin the session.
struct StartSessionIntent: LiveActivityIntent {
    static var title: LocalizedStringResource = "Start morning session"
    static var openAppWhenRun = true
    func perform() async throws -> some IntentResult {
        UserDefaults.standard.set(true, forKey: startKey)
        return .result()
    }
}

/// Sends the mic and plays the bot as 16 kHz 16-bit mono PCM over a WebSocket.
@MainActor final class Session: ObservableObject {
    @Published var state = "Ready"
    @Published var speaker = false { didSet { route() } }
    private var socket: URLSessionWebSocketTask?
    private var ending = false
    private let engine = AVAudioEngine()
    private let player = AVAudioPlayerNode()
    private let wire = AVAudioFormat(commonFormat: .pcmFormatInt16, sampleRate: 16000, channels: 1, interleaved: true)!
    private let play = AVAudioFormat(commonFormat: .pcmFormatFloat32, sampleRate: 24000, channels: 1, interleaved: false)!

    @Published var live = false
    @Published var began = Date()

    func start(stages: String) {
        guard socket == nil else { return }
        state = "Connecting"
        live = true
        began = .now
        do {
            let audio = AVAudioSession.sharedInstance()
            try audio.setCategory(.playAndRecord, mode: .default, options: [.allowBluetoothHFP])
            try audio.setActive(true)
            route()
            let task = URLSession.shared.webSocketTask(with: URL(string: serverBase + stages)!)
            socket = task
            task.resume()
            let input = engine.inputNode
            let mic = input.outputFormat(forBus: 0)
            let convert = AVAudioConverter(from: mic, to: wire)!
            input.installTap(onBus: 0, bufferSize: 1600, format: mic) { [wire] buffer, _ in
                let cap = AVAudioFrameCount(Double(buffer.frameLength) * 16000 / mic.sampleRate) + 16
                guard let out = AVAudioPCMBuffer(pcmFormat: wire, frameCapacity: cap) else { return }
                var used = false
                convert.convert(to: out, error: nil) { _, status in
                    if used { status.pointee = .noDataNow; return nil }
                    used = true; status.pointee = .haveData; return buffer
                }
                let data = Data(bytes: out.int16ChannelData![0], count: Int(out.frameLength) * 2)
                task.send(.data(data)) { _ in }
            }
            engine.attach(player)
            engine.connect(player, to: engine.mainMixerNode, format: play)
            try engine.start()
            player.play()
            route()  // starting the engine can reset the output
            state = "Connected"
            receive()
            watchLine(task)
        } catch {
            state = "Couldn't start audio"
            stop()
        }
    }

    /// A dead network sends no close, so ping to notice it.
    private func watchLine(_ task: URLSessionWebSocketTask) {
        Task {
            while socket === task {
                try? await Task.sleep(for: .seconds(pingEvery))
                guard socket === task else { return }
                task.sendPing { [weak self] error in
                    if error != nil { Task { @MainActor in self?.dropped() } }
                }
            }
        }
    }

    /// The line died: say so out loud, then shut down.
    private func dropped() {
        guard socket != nil, !ending else { return }
        ending = true
        state = "Session dropped"
        for _ in 0..<3 { enqueueTone() }
        Task {
            try? await Task.sleep(for: .seconds(2))
            ending = false
            stop()
            state = "Session dropped"
        }
    }

    private func enqueueTone() {
        let rate = play.sampleRate, n = AVAudioFrameCount(rate * 0.45)
        guard let buf = AVAudioPCMBuffer(pcmFormat: play, frameCapacity: n) else { return }
        buf.frameLength = n
        for i in 0..<Int(n) {
            let t = Double(i) / rate
            buf.floatChannelData![0][i] = t < 0.25 ? Float(sin(2 * .pi * 480 * t)) * 0.5 : 0
        }
        player.scheduleBuffer(buf)
    }

    func skipToCheckIn() { socket?.send(.string("skip")) { _ in } }

    private func receive() {
        socket?.receive { [weak self] result in
            Task { @MainActor in
                guard let self else { return }
                switch result {
                case .success(.data(let data)): self.enqueue(data); self.receive()
                case .success: self.receive()
                case .failure: self.dropped()
                }
            }
        }
    }

    private func enqueue(_ data: Data) {
        let n = data.count / 2
        guard n > 0, let buf = AVAudioPCMBuffer(pcmFormat: play, frameCapacity: AVAudioFrameCount(n)) else { return }
        buf.frameLength = AVAudioFrameCount(n)
        data.withUnsafeBytes { raw in
            let s = raw.bindMemory(to: Int16.self)
            for i in 0..<n { buf.floatChannelData![0][i] = max(-1, min(1, Float(s[i]) / 32768 * voiceGain)) }
        }
        player.scheduleBuffer(buf)
    }

    /// Speaker, or earpiece with the screen going dark against your face.
    private func route() {
        guard live else { return }
        try? AVAudioSession.sharedInstance().overrideOutputAudioPort(speaker ? .speaker : .none)
        UIDevice.current.isProximityMonitoringEnabled = live && !speaker
    }

    func stop() {
        UIDevice.current.isProximityMonitoringEnabled = false
        socket?.cancel(); socket = nil
        live = false
        state = "Ended"
        if engine.isRunning { engine.inputNode.removeTap(onBus: 0); engine.stop() }
        player.stop()
        try? AVAudioSession.sharedInstance().setActive(false)
    }
}

/// The in-session screen, laid out like a phone call.
struct CallView: View {
    @ObservedObject var session: Session

    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: "sunrise.fill").font(.system(size: 56)).foregroundStyle(.indigo).padding(.top, 80)
            Text("Morning").font(.largeTitle.weight(.semibold))
            TimelineView(.periodic(from: .now, by: 1)) { ctx in
                Text(Duration.seconds(max(0, ctx.date.timeIntervalSince(session.began))).formatted(.time(pattern: .minuteSecond)))
                    .monospacedDigit().foregroundStyle(.secondary)
            }
            Text(session.state).font(.footnote).foregroundStyle(.secondary)
            Spacer()
            HStack(spacing: 48) {
                CallButton(icon: session.speaker ? "speaker.wave.3.fill" : "speaker.fill", label: "Speaker", on: session.speaker) {
                    session.speaker.toggle()
                }
                CallButton(icon: "forward.end.fill", label: "Skip to check-in", on: false) { session.skipToCheckIn() }
            }
            Button { session.stop() } label: {
                Image(systemName: "phone.down.fill").font(.title).foregroundStyle(.white)
                    .frame(width: 76, height: 76).background(.red, in: Circle())
            }
            .accessibilityLabel("Hang up")
            .padding(.top, 36).padding(.bottom, 56)
        }
        .frame(maxWidth: .infinity)
    }
}

struct CallButton: View {
    let icon: String, label: String, on: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 8) {
                Image(systemName: icon).font(.title2).frame(width: 64, height: 64)
                    .foregroundStyle(on ? Color(.systemBackground) : .primary)
                    .background(on ? Color.primary : Color(.secondarySystemFill), in: Circle())
                Text(label).font(.caption).foregroundStyle(.secondary).multilineTextAlignment(.center)
            }.frame(width: 96)
        }.buttonStyle(.plain)
    }
}

struct ContentView: View {
    @StateObject private var session = Session()
    @Environment(\.scenePhase) private var phase
    @AppStorage("wakeTime") private var wake = Date().timeIntervalSince1970
    @AppStorage("breathe") private var breathe = false
    @AppStorage("meditate") private var meditate = false
    @AppStorage("checkin") private var checkin = true
    @AppStorage("voice") private var voice = "marian"
    @AppStorage("speed") private var speed = 25.0
    @State private var voices = [Voice(id: "marian", name: "Marian")]
    @State private var note = ""
    @StateObject private var place = Place()

    var body: some View {
        NavigationStack {
            Form {
                Section("Wake-up alarm") {
                    DatePicker("Time", selection: Binding(get: { Date(timeIntervalSince1970: wake) },
                                                          set: { wake = $0.timeIntervalSince1970 }),
                               displayedComponents: .hourAndMinute)
                    Button { Task { await setAlarm() } } label: { Label("Set alarm", systemImage: "alarm") }
                    if !note.isEmpty { Text(note).foregroundStyle(.secondary) }
                }
                Section("Stages") {
                    Toggle(isOn: $breathe) { Label("Breathing", systemImage: "wind") }
                    Toggle(isOn: $meditate) { Label("Meditation", systemImage: "leaf") }
                    Toggle(isOn: $checkin) { Label("Check-in", systemImage: "bubble.left.and.bubble.right") }
                }
                Section("Voice") {
                    Picker(selection: $voice) {
                        ForEach(voices, id: \.id) { Text($0.name).tag($0.id) }
                    } label: { Label("Voice", systemImage: "person.wave.2") }
                    LabeledContent {
                        Slider(value: $speed, in: 0...60, step: 5)
                    } label: { Label("Speed \(Int(speed + 100))%", systemImage: "speedometer") }
                }
                Section("Session") {
                    Button { begin() } label: { Label("Start now", systemImage: "sunrise") }
                    Toggle(isOn: $session.speaker) { Label("Speaker", systemImage: "speaker.wave.2") }
                    Button { place.saveHome() } label: {
                        Label(place.hasHome ? "Update home to here" : "Set home to here", systemImage: "house")
                    }
                    if !place.status.isEmpty { Text(place.status).foregroundStyle(.secondary) }
                    Label(session.state, systemImage: session.live ? "waveform" : "circle")
                        .foregroundStyle(.secondary)
                }
            }
            .navigationTitle("Morning")
            .task { await loadVoices() }
            .fullScreenCover(isPresented: $session.live) { CallView(session: session) }
        }
        .onChange(of: phase) { _, now in
            if now == .active, UserDefaults.standard.bool(forKey: startKey) {
                UserDefaults.standard.set(false, forKey: startKey)
                begin()
            }
        }
    }

    private func loadVoices() async {
        let url = URL(string: "http://\(serverHost):8798/voices")!
        if let (data, _) = try? await URLSession.shared.data(from: url),
           let list = try? JSONDecoder().decode([Voice].self, from: data), !list.isEmpty { voices = list }
    }

    private func begin() {
        let on = [("breathe", breathe), ("meditate", meditate), ("checkin", checkin)].filter(\.1).map(\.0)
        session.start(stages: on.joined(separator: ",") + "&voice=\(voice)&speed=\(Int(speed))")
    }

    private func setAlarm() async {
        do {
            guard try await AlarmManager.shared.requestAuthorization() == .authorized else {
                note = "Alarms are turned off for Morning in Settings."; return
            }
            let cal = Calendar.current
            let parts = cal.dateComponents([.hour, .minute], from: Date(timeIntervalSince1970: wake))
            let date = cal.nextDate(after: .now, matching: parts, matchingPolicy: .nextTime)!
            let alert = AlarmPresentation.Alert(
                title: "Good morning",
                stopButton: AlarmButton(text: "Stop", textColor: .white, systemImageName: "stop.fill"),
                secondaryButton: AlarmButton(text: "Start", textColor: .white, systemImageName: "sunrise.fill"),
                secondaryButtonBehavior: .custom)
            let attrs = AlarmAttributes<WakeMeta>(presentation: AlarmPresentation(alert: alert), tintColor: .indigo)
            let config = AlarmManager.AlarmConfiguration<WakeMeta>(
                schedule: .fixed(date), attributes: attrs, secondaryIntent: StartSessionIntent())
            for alarm in try AlarmManager.shared.alarms { try? AlarmManager.shared.cancel(id: alarm.id) }
            _ = try await AlarmManager.shared.schedule(id: UUID(), configuration: config)
            note = "Set for " + date.formatted(date: .abbreviated, time: .shortened)
        } catch { note = "Couldn't set it: \(error.localizedDescription)" }
    }
}

@main struct MorningApp: App {
    var body: some Scene { WindowGroup { ContentView() } }
}
