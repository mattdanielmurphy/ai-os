// Run an audio file through a chain of Audio Unit effects (FabFilter etc.), offline and silent.
//   swift fx.swift chain.json in.wav out.wav       chain.json: [{"au": "aumf:FPSr:FabF", "params": {"Threshold": -30}}]
//   swift fx.swift --list aumf:FC2p:FabF            print the AU's parameter names, ranges and current values
// Same AU loading and set-by-display-name approach as ~/projects/claude-ambient/render_mix.swift.
import AVFoundation

struct FX: Codable { let au: String; let params: [String: Double]? }

func fourcc(_ s: String) -> OSType { s.utf8.reduce(0) { ($0 << 8) | OSType($1) } }
func load(_ spec: String) -> AVAudioUnit {
    let p = spec.split(separator: ":").map(String.init)
    let d = AudioComponentDescription(componentType: fourcc(p[0]), componentSubType: fourcc(p[1]),
                                      componentManufacturer: fourcc(p[2]), componentFlags: 0, componentFlagsMask: 0)
    let sem = DispatchSemaphore(value: 0); var unit: AVAudioUnit?
    AVAudioUnit.instantiate(with: d, options: []) { u, e in unit = u; if let e { print("instantiate error", spec, e) }; sem.signal() }
    sem.wait()
    guard let unit else { print("could not load", spec); exit(1) }
    return unit
}

let args = CommandLine.arguments
if args.count == 3 && args[1] == "--list" {
    let u = load(args[2])
    for p in u.auAudioUnit.parameterTree?.allParameters ?? [] {
        print("\(p.displayName)\t\(p.minValue)…\(p.maxValue)\t= \(p.value)\t\(p.unitName ?? "")")
    }
    exit(0)
}
guard args.count == 4 else { print("usage: swift fx.swift chain.json in.wav out.wav | --list <au>"); exit(2) }
let chain = try JSONDecoder().decode([FX].self, from: Data(contentsOf: URL(fileURLWithPath: args[1])))
let input = try AVAudioFile(forReading: URL(fileURLWithPath: args[2]))
let format = input.processingFormat

let engine = AVAudioEngine()
let player = AVAudioPlayerNode()
engine.attach(player)
var tail: AVAudioNode = player
for fx in chain {
    let u = load(fx.au); engine.attach(u)
    for (name, v) in fx.params ?? [:] {
        guard let p = u.auAudioUnit.parameterTree?.allParameters.first(where: { $0.displayName == name }) else {
            print("  no param '\(name)' on", u.name); continue
        }
        p.value = AUValue(v)
    }
    engine.connect(tail, to: u, format: format); tail = u
}
engine.connect(tail, to: engine.mainMixerNode, format: format)
try engine.enableManualRenderingMode(.offline, format: format, maximumFrameCount: 4096)
try engine.start()
player.scheduleFile(input, at: nil)
player.play()

let out = try AVAudioFile(forWriting: URL(fileURLWithPath: args[3]), settings: format.settings)
let buf = AVAudioPCMBuffer(pcmFormat: engine.manualRenderingFormat, frameCapacity: 4096)!
let total = input.length + AVAudioFramePosition(format.sampleRate * 3)  // + reverb tail
while engine.manualRenderingSampleTime < total {
    let n = min(AVAudioFrameCount(total - engine.manualRenderingSampleTime), 4096)
    guard try engine.renderOffline(n, to: buf) == .success else { break }
    try out.write(from: buf)
}
print("wrote", args[3])
