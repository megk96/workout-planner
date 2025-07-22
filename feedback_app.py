from flask import Flask, request, render_template
from notion_integration import update_feedback

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def feedback():
    if request.method == "POST":
        status = request.form.get("status", "Completed")
        feedback_data = {
            "video_id": request.form.get("video_id", "dQw4w9WgXcQ"),
            "note": request.form.get("note", "").strip(),
            "status": status,
        }

        # Only include detailed feedback if completed
        if status == "Completed":
            feedback_data.update({
                "types": request.form.get("types", "").split(",") if request.form.get("types") else [],
                "muscles_weak": request.form.get("muscles_weak", "").split(",") if request.form.get("muscles_weak") else [],
                "mood": request.form.get("mood", "").split(",") if request.form.get("mood") else [],
                "effort": int(request.form.get("effort", 0) or 0),
                "effectiveness": int(request.form.get("effectiveness", 0) or 0),
            })

        try:
            update_feedback(feedback_data["video_id"], feedback_data)
            return "✅ Feedback submitted. Notion updated."
        except ValueError as e:
            return f"❌ Error: {str(e)}"
        except Exception as e:
            print(e)
            return "❌ An unexpected error occurred while saving feedback."

    # GET method: retrieve video_id from query string
    video_id = request.args.get("video_id", "dQw4w9WgXcQ")
    return render_template("feedback.html", video_id=video_id)