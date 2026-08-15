use std::io;
use crossterm::{
    event::{self, DisableMouseCapture, EnableMouseCapture, Event, KeyCode},
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};
use ratatui::{
    backend::CrosstermBackend,
    layout::{Constraint, Direction, Layout},
    style::{Color, Modifier, Style},
    text::{Line, Span},
    widgets::{Block, Borders, Paragraph},
    Terminal,
};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let home = aios_core::pty::get_ai_os_home();
    println!("Starting AI-OS TUI (Home: {})...", home.display());

    enable_raw_mode()?;
    let mut stdout = io::stdout();
    execute!(stdout, EnterAlternateScreen, EnableMouseCapture)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    let mut running = true;
    while running {
        terminal.draw(|f| {
            let chunks = Layout::default()
                .direction(Direction::Vertical)
                .constraints([
                    Constraint::Length(3),
                    Constraint::Min(1),
                    Constraint::Length(3),
                ])
                .split(f.area());

            let header = Paragraph::new(Line::from(vec![
                Span::styled("AI-OS ", Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD)),
                Span::styled("Terminal Harness (Headless Mode)", Style::default().fg(Color::White)),
            ]))
            .block(Block::default().borders(Borders::ALL).title(" AI-OS TUI "));
            f.render_widget(header, chunks[0]);

            let body = Paragraph::new(vec![
                Line::from("Connected to aios-core backend."),
                Line::from("Press 'q' or 'Esc' to exit to shell."),
            ])
            .block(Block::default().borders(Borders::ALL).title(" Status "));
            f.render_widget(body, chunks[1]);

            let footer = Paragraph::new("Press 'q' to quit | 'r' to refresh")
                .style(Style::default().fg(Color::DarkGray))
                .block(Block::default().borders(Borders::ALL));
            f.render_widget(footer, chunks[2]);
        })?;

        if event::poll(std::time::Duration::from_millis(100))? {
            if let Event::Key(key) = event::read()? {
                if matches!(key.code, KeyCode::Char('q') | KeyCode::Esc) {
                    running = false;
                }
            }
        }
    }

    disable_raw_mode()?;
    execute!(
        terminal.backend_mut(),
        LeaveAlternateScreen,
        DisableMouseCapture
    )?;
    terminal.show_cursor()?;

    println!("AI-OS TUI exited cleanly.");
    Ok(())
}
