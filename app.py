from flask import Flask, request, jsonify
import instaloader

app = Flask(__name__)

@app.route('/download_posts', methods=['POST'])
def download_posts():
    # Get Instagram credentials and target profile from the request
    data = request.json
    username = data.get('username')
    password = data.get('password')
    target_profile = data.get('target_profile')

    if not username or not password or not target_profile:
        return jsonify({"error": "Username, password, and target profile must be provided"}), 400

    try:
        # Create an instance of Instaloader
        loader = instaloader.Instaloader()

        # Log in to your Instagram account
        loader.login(username, password)

        # Specify the target Instagram account
        profile = instaloader.Profile.from_username(loader.context, target_profile)

        # Iterate through each post in the profile
        posts_data = []
        for post in profile.get_posts():
            # Download the post
            loader.download_post(post, target=profile.username)

            # Collect post details
            post_details = {
                "shortcode": post.shortcode,
                "caption": post.caption,
                "hashtags": post.caption_hashtags,
                "mentions": post.caption_mentions,
                "location": post.location.name if post.location else "None",
                "date": post.date.isoformat(),
                "likes": post.likes,
                "comments_count": post.comments,
                "is_video": post.is_video,
                "video_url": post.video_url if post.is_video else "None",
                "song": post.title if post.title else "None",
            }
            posts_data.append(post_details)

            # Save comments and other post details in a text file
            with open(f"{post.shortcode}_details.txt", "w", encoding="utf-8") as f:
                # Write post details
                for key, value in post_details.items():
                    f.write(f"{key}: {value}\n")
                
                # Write comments
                f.write("\nComments:\n")
                for comment in post.get_comments():
                    f.write(f"{comment.owner.username}: {comment.text}\n")

        return jsonify({"message": "Posts downloaded successfully", "posts_data": posts_data})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
