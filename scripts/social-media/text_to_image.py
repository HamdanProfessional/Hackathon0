#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Text to Image Generator for Instagram

Converts text post into an image that can be uploaded to Instagram.
Handles text wrapping, fonts, and styling automatically.

Usage:
    python text_to_image.py "Your post text here" --output post_image.png
"""

import argparse
import textwrap
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("PIL not installed. Run: pip install Pillow")
    import sys
    sys.exit(1)


def create_text_image(text, output_path="post_image.png", bg_color="#1a1a2e", text_color="#ffffff", accent_color="#4cc9f0"):
    """
    Create an image from text with modern styling.

    Args:
        text: The text content
        output_path: Where to save the image
        bg_color: Background color (default: dark blue)
        text_color: Text color (default: white)
        accent_color: Accent color for highlights (default: cyan)

    Returns:
        Path to saved image
    """
    # Image dimensions (Instagram square)
    width = 1080
    height = 1080

    # Create image with gradient background
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    # Create gradient background
    for y in range(height):
        # Gradient from top to bottom
        r1, g1, b1 = int(bg_color[1:3], 16), int(bg_color[3:5], 16), int(bg_color[5:7], 16)
        r2, g2, b2 = 26, 26, 46  # Darker at bottom
        ratio = y / height
        r = int(r1 * (1 - ratio) + r2 * ratio)
        g = int(g1 * (1 - ratio) + g2 * ratio)
        b = int(b1 * (1 - ratio) + b2 * ratio)
        draw.rectangle([(0, y), (width, y + 1)], fill=(r, g, b))

    # Padding
    padding = 80
    content_width = width - 2 * padding

    try:
        # Try to use a nice font
        font_large = ImageFont.truetype("arial.ttf", 48)
        font_medium = ImageFont.truetype("arial.ttf", 40)
        font_small = ImageFont.truetype("arial.ttf", 32)
    except:
        # Fallback to default font
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Current y position
    y = padding

    # Add title/first line with accent color
    lines = text.split('\n')
    if lines:
        # Draw first line larger
        first_line = lines[0]
        if len(first_line) < 50:
            # Draw as title
            draw.text((padding, y), first_line, fill=accent_color, font=font_large)
            y += 70
            remaining_text = '\n'.join(lines[1:])
        else:
            remaining_text = text

        # Wrap and draw remaining text
        if remaining_text:
            # Remove emojis that might not render
            import re
            # Simple approach: keep text, remove problematic chars
            clean_text = remaining_text

            paragraphs = clean_text.split('\n\n')
            for paragraph in paragraphs:
                # Wrap text to fit width
                wrapped_lines = textwrap.wrap(paragraph, width=25)

                for line in wrapped_lines:
                    if y + 50 > height - padding:
                        # Image is full, stop adding text
                        break

                    draw.text((padding, y), line, fill=text_color, font=font_medium)
                    y += 55

                y += 30  # Paragraph spacing

    # Add footer branding
    footer_y = height - padding - 50
    try:
        footer_font = ImageFont.truetype("arial.ttf", 28)
    except:
        footer_font = ImageFont.load_default()

    draw.text((padding, footer_y), "Built with AI Employee", fill=accent_color, font=footer_font)

    # Save image
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    img.save(output)

    print(f"✅ Image created: {output}")
    return output


def main():
    parser = argparse.ArgumentParser(description="Convert text to Instagram image")
    parser.add_argument("text", help="Text content")
    parser.add_argument("--output", default="post_image.png", help="Output image path")
    parser.add_argument("--bg", default="#1a1a2e", help="Background color")
    parser.add_argument("--text-color", default="#ffffff", help="Text color")
    parser.add_argument("--accent", default="#4cc9f0", help="Accent color")

    args = parser.parse_args()

    create_text_image(
        args.text,
        args.output,
        args.bg,
        args.text_color,
        args.accent
    )


if __name__ == "__main__":
    main()
