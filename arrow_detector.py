import cv2
import numpy as np


def convert_pil_to_ocv(image):
    return np.array(image)


def get_arrow_direction(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (3, 3), 1)

    # Detect edges using Canny edge detector
    edges = cv2.Canny(blurred, 50, 150)

    # Find contours in the edge-detected image
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Iterate over contours to find the arrow
    for contour in contours:
        # Approximate the contour
        epsilon = 0.03 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Check if the contour has 7 vertices, which is typical for an arrow shape
        if len(approx) > 7:
            # Get the bounding rectangle of the contour
            x, y, w, h = cv2.boundingRect(approx)

            # Define the direction based on the aspect ratio
            aspect_ratio = float(w) / h
            if aspect_ratio > 1:
                # Arrow is pointing left or right
                if approx[0][0][0] < approx[3][0][0]:
                    direction = 4 #"left"
                else:
                    direction = 0 #"right"
            else:
                # Arrow is pointing up or down
                if approx[0][0][1] < approx[3][0][1]:
                    direction = 6 #"up"
                else:
                    direction = 2 #"down"

            return direction