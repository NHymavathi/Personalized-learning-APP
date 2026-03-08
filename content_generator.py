def generate_learning_content(topic, level, learning_style, interests, accuracy):
    content = {
        "topic": topic.title(),
        "level": level.title(),

        "explanation": f"""
{topic.title()} is an important subject that plays a key role in modern technology and problem-solving.
At a {level.lower()} level, learners focus on understanding core concepts, real-world usage,
and how {topic.lower()} is applied in practical scenarios.
This content is tailored for {learning_style.lower()} learning with approximately {accuracy}% accuracy.
""",

        "key_topics": [
            f"Introduction to {topic}",
            f"Core concepts of {topic}",
            f"{topic} fundamentals",
            f"Advanced concepts in {topic}",
            f"Real-world applications of {topic}",
            f"Best practices in {topic}"
        ],

        "practice_tasks": [
            f"Identify real-life use cases of {topic}",
            f"Compare {topic} with related technologies",
            f"Design a small project using {topic}"
        ],

        "next_steps": [
            f"Practice {topic} through mini-projects",
            f"Explore advanced {topic} concepts",
            f"Apply {topic} in real-world applications"
        ],

        "resources": [
            {
                "title": f"{topic} Tutorial",
                "website": "W3Schools",
                "url": f"https://www.w3schools.com/{topic.lower()}/",
                "purpose": "Beginner-friendly explanations"
            },
            {
                "title": f"{topic} Guide",
                "website": "GeeksforGeeks",
                "url": f"https://www.geeksforgeeks.org/{topic.lower()}/",
                "purpose": "Concept clarity with examples"
            }
        ]
    }

    return content