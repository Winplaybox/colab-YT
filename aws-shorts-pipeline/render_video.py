"""
Render Video using EpicBharatSaga Video Producer
"""
import os
import sys

eb_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "channels", "EpicBharatSaga"))
sys.path.insert(0, eb_dir)

from video_producer import produce_train_video

def render_story_video(story_json_path, quality="1080p"):
    print(f"\n[RENDER] Initiating video render for: {story_json_path}")
    output_path = produce_train_video(story_json_path, quality=quality)
    print(f"\n[RENDER COMPLETE] Video saved at: {output_path}")
    return output_path

if __name__ == "__main__":
    test_json = os.path.join(eb_dir, "stories", "shiva_aws_a63d2e02.json")
    render_story_video(test_json)
