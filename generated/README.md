# Generated Content Archive

This folder contains all generated news briefs for testing and version control.

## Structure

```
generated/
├── scripts/
│   ├── working/          # Latest working scripts
│   └── archive/          # Historical versions
├── audio/
│   ├── working/          # Latest working audio files  
│   └── archive/          # Historical versions
└── metadata/
    ├── working/          # Latest working metadata
    └── archive/          # Historical versions
```

## Naming Convention

- **Scripts**: `YYYY-MM-DD_HH-MM_model-name_script.txt`
- **Audio**: `YYYY-MM-DD_HH-MM_voice-name_audio.mp3`
- **Metadata**: `YYYY-MM-DD_HH-MM_metadata.json`

## Quality Levels

- **working/**: Current best versions (Claude + Joanna)
- **archive/**: Historical versions for reference

## Current Best Configuration

- **Model**: Claude 3 Haiku (anthropic.claude-3-haiku-20240307-v1:0)
- **Voice**: Joanna Neural
- **Style**: AM Podcast international news
- **Region**: us-west-2