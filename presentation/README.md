# OpenClawtype ManimGL Presentation

This folder contains a short animated presentation for the workshop, written
for the original 3Blue1Brown ManimGL project.

3b1b/manim is installed as `manimgl` and imported as `manimlib`, not as
`manim`. See: https://github.com/3b1b/manim

## Render

Install ManimGL in an environment with FFmpeg and OpenGL support:

```bash
pip install manimgl
```

Render one scene:

```bash
manimgl presentation/openclawtype_manim.py ArchitectureScene -w
```

Preview a final frame:

```bash
manimgl presentation/openclawtype_manim.py TelegramConnectorScene -s
```

Useful scenes:

- `TitleScene`
- `ArchitectureScene`
- `ConnectorStepScene`
- `TelegramConnectorScene`
- `WorkshopFlowScene`

