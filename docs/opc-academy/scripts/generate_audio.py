#!/usr/bin/env python3
"""Batch TTS generation for OPC Academy courses using Edge TTS (zh-CN-YunxiNeural).
Quality: MP3, 24kHz, mono — matching Kongbo standard."""
import subprocess, os, re, sys, json

COURSES_DIR = os.path.expanduser("~/Desktop/OPC/opc-platform/docs/opc-academy/courses")
AUDIO_DIR = os.path.expanduser("~/Desktop/OPC/opc-platform/docs/opc-academy/audio")

VOICE = "zh-CN-YunxiNeural"

FILES = [
    ("01-opc-one-person-company-basics", "01-opc-one-person-company-basics"),
    ("02-hermes-agent-setup", "02-hermes-agent-setup"),
    ("03-hermes-skills-system", "03-hermes-skills-system"),
    ("04-multi-agent-orchestration", "04-multi-agent-orchestration"),
    ("05-knowledge-management", "05-knowledge-management"),
    ("06-automation-workflows", "06-automation-workflows"),
    ("07-private-domain-growth", "07-private-domain-growth"),
    ("08-monetization-models", "08-monetization-models"),
    ("09-kondratiev-ai-cycles", "09-kondratiev-ai-cycles"),
    ("10-opc-masterclass", "10-opc-masterclass"),
]

def extract_text(md_path):
    """Extract readable text from markdown, stripping technical markers."""
    with open(md_path, 'r') as f:
        text = f.read()
    # Remove YAML frontmatter
    text = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.DOTALL)
    # Remove markdown syntax markers but keep content
    text = re.sub(r'^#{1,4}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    text = re.sub(r'^[-*]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'---', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def generate_audio(name, text, output_mp3):
    """Generate TTS audio: text → Edge TTS → ffmpeg → MP3 24kHz mono."""
    tmp_wav = f"/tmp/tts_{name}.wav"
    
    # Generate with edge-tts (pipe to ffmpeg for direct conversion)
    cmd = [
        "edge-tts",
        "--voice", VOICE,
        "--text", text,
        "--write-media", tmp_wav,
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        print(f"  ✗ edge-tts failed: {result.stderr[-200:]}")
        return False
    
    # Convert to MP3 24kHz mono (Kongbo standard)
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-i", tmp_wav,
        "-ac", "1",
        "-ar", "24000",
        "-b:a", "48k",
        output_mp3
    ]
    result2 = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=60)
    if result2.returncode != 0:
        print(f"  ✗ ffmpeg failed: {result2.stderr[-200:]}")
        return False
    
    # Cleanup
    os.remove(tmp_wav)
    
    # Report size
    size_mb = os.path.getsize(output_mp3) / 1024 / 1024
    print(f"  ✓ {size_mb:.2f} MB")
    return True

def main():
    total = len(FILES)
    for i, (md_name, audio_name) in enumerate(FILES, 1):
        md_path = os.path.join(COURSES_DIR, f"{md_name}.md")
        output_mp3 = os.path.join(AUDIO_DIR, f"{audio_name}.mp3")
        
        char_count = len(open(md_path).read())
        print(f"[{i}/{total}] {audio_name}.mp3 ({char_count} chars)...", flush=True)
        
        text = extract_text(md_path)
        if not text:
            print(f"  ✗ Empty text after extraction")
            continue
        
        # edge-tts has a text length limit — split into chunks if needed
        # The practical limit is ~3000 chars per call
        if len(text) > 2500:
            chunks = []
            paragraphs = text.split('\n\n')
            current = ""
            for p in paragraphs:
                if len(current) + len(p) < 2500:
                    current += p + "\n\n"
                else:
                    if current:
                        chunks.append(current.strip())
                    current = p + "\n\n"
            if current:
                chunks.append(current.strip())
            
            # Generate each chunk, then concatenate
            tmp_files = []
            for j, chunk in enumerate(chunks):
                tmp_wav = f"/tmp/tts_{audio_name}_chunk{j}.wav"
                cmd = ["edge-tts", "--voice", VOICE, "--text", chunk, "--write-media", tmp_wav]
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                if r.returncode != 0:
                    print(f"  ✗ Chunk {j} failed: {r.stderr[-100:]}")
                    break
                tmp_files.append(tmp_wav)
            
            if len(tmp_files) == len(chunks):
                # Concatenate with ffmpeg
                concat_list = "/tmp/tts_concat.txt"
                with open(concat_list, 'w') as f:
                    for tf in tmp_files:
                        f.write(f"file '{tf}'\n")
                
                concat_cmd = [
                    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", concat_list,
                    "-ac", "1", "-ar", "24000", "-b:a", "48k",
                    output_mp3
                ]
                r2 = subprocess.run(concat_cmd, capture_output=True, text=True, timeout=120)
                
                # Cleanup
                for tf in tmp_files:
                    os.remove(tf) if os.path.exists(tf) else None
                os.remove(concat_list) if os.path.exists(concat_list) else None
                
                if r2.returncode == 0:
                    size_mb = os.path.getsize(output_mp3) / 1024 / 1024
                    print(f"  ✓ {len(chunks)} chunks → {size_mb:.2f} MB", flush=True)
                else:
                    print(f"  ✗ Concat failed: {r2.stderr[-200:]}")
            else:
                # Cleanup partials
                for tf in tmp_files:
                    os.remove(tf) if os.path.exists(tf) else None
        else:
            generate_audio(audio_name, text, output_mp3)
    
    # Summary
    total_mb = sum(os.path.getsize(os.path.join(AUDIO_DIR, f)) for f in os.listdir(AUDIO_DIR) if f.endswith('.mp3')) / 1024 / 1024
    count = len([f for f in os.listdir(AUDIO_DIR) if f.endswith('.mp3')])
    print(f"\n✅ Done: {count}/10 files, {total_mb:.1f} MB total", flush=True)

if __name__ == "__main__":
    main()
