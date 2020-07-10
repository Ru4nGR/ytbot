from random import randrange, seed
import moviepy.editor as editor
import os

def makeVideo(dir, name, clipFiles, transitionInFiles, transitionOutFiles, width, height, fps):
    seed()
    
    intros = [editor.VideoFileClip(transitionInFile, has_mask=True).resize((width, height)) for transitionInFile in transitionInFiles]
    outros = [editor.VideoFileClip(transitionOutFile, has_mask=True).resize((width, height)) for transitionOutFile in transitionOutFiles]
    clips = [editor.VideoFileClip(clipFile).resize((width, height)) for clipFile in clipFiles]

    compositedClips = []

    for clip in clips:
        intro = randrange(len(intros))
        outro = randrange(len(outros))
        compositedClips.append(editor.CompositeVideoClip([
            clip,
            intros[intro],
            outros[outro].set_start(clip.duration - outros[outro].duration)
        ]))

    out = editor.concatenate_videoclips(compositedClips)
    out.fps = fps

    if not os.path.isdir(dir):
        os.makedirs(dir)
    path = f'{dir}/{name}.mp4'
    out.write_videofile(path)

    return path