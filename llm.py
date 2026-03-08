def generate_learning_material(topic, profile):

    style = profile.get("learning_style", "reading")

    content = f"""
Topic: {topic}

Learning Style: {style}

Explanation:
{topic.capitalize()} is an important concept in computer science and technology.

Step-by-step learning:

1. Understand the basic concepts of {topic}
2. Practice simple examples
3. Build small projects
4. Explore advanced topics

Recommended Practice:
• Solve coding exercises
• Read documentation
• Build mini applications
"""

    return content