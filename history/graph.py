#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np


# Define the hockey-stick function (piecewise cubic with transition at x = 10)
def hockey_stick(x):
    return np.piecewise(
        x,
        [x < 10, x >= 10],
        [
            lambda x: 0.05 * x,
            lambda x: 0.005 * (x - 10) ** 3 + 0.5,
        ],  # Transition at x = 10
    )


# Define the fixed-point (logistic growth) function
def fixed_point(x):
    return 1 / (
        1 + np.exp(-0.6 * (x - 5))
    )  # Logistic growth centered around x = 5


# Define the decay function (damped sine wave)
def decay(x):
    return np.sin(0.5 * x) * np.exp(-0.1 * x)  # Damped sine wave


# Introduce larger noise (jitter) for better differentiation between metrics
noise_factor = 0.05  # Increased noise

# Use a fixed X-axis range for all plots (e.g., 0 to 20)
time_range = np.linspace(0, 20, 500)


# Function to adjust label placement dynamically
def get_label_offset(x, y, ax):
    # Get the current axis limits
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    # Determine where to place the label based on the position in the graph
    if x < (xlim[0] + xlim[1]) / 2:
        x_offset = 1  # Right
    else:
        x_offset = -2  # Left

    if y < (ylim[0] + ylim[1]) / 2:
        y_offset = 0.1  # Above
    else:
        y_offset = -0.1  # Below

    return x_offset, y_offset


# Create plots for each function (hockey-stick, fixed-point, decay)
for performance_function, title, file_name, custom_labels in [
    (
        hockey_stick,
        "Hockey-Stick Growth",
        "hockey-stick.svg",
        [("Inflection Point", 12.5)],
    ),
    (
        fixed_point,
        "Saturation (Fixed-Point) Growth",
        "fixed-point.svg",
        [("Saturation", 10)],
    ),
    (
        decay,
        "Decay Over Time",
        "decay.svg",
        [("Initial Growth", 2.5), ("Decline", 8.75), ("Recovery", 15)],
    ),
]:

    # Generate performance metrics with noise
    accuracy = performance_function(
        time_range
    ) + noise_factor * np.random.normal(size=len(time_range))
    generalization = (
        performance_function(time_range)
        + noise_factor * np.random.normal(size=len(time_range))
        + 0.1
    )
    coherence = (
        performance_function(time_range)
        + noise_factor * np.random.normal(size=len(time_range))
        + 0.15
    )
    creativity = (
        performance_function(time_range)
        + noise_factor * np.random.normal(size=len(time_range))
        + 0.2
    )
    efficiency = (
        performance_function(time_range)
        + noise_factor * np.random.normal(size=len(time_range))
        + 0.25
    )

    # Plot the time-series data with noise to differentiate the lines
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(time_range, accuracy, label="Accuracy", color="blue", linewidth=2)
    ax.plot(
        time_range,
        generalization,
        label="Generalization",
        color="green",
        linewidth=2,
    )
    ax.plot(
        time_range, coherence, label="Coherence", color="orange", linewidth=2
    )
    ax.plot(
        time_range, creativity, label="Creativity", color="red", linewidth=2
    )
    ax.plot(
        time_range, efficiency, label="Efficiency", color="purple", linewidth=2
    )

    # Add custom labels for each graph with dynamically adjusted annotations
    for label, x in custom_labels:
        y = performance_function(np.array([x]))[0]

        # Add a black dot with a white edge
        ax.scatter(
            x,
            y,
            color="black",
            zorder=5,
            edgecolor="white",  # White edge
            linewidth=2,  # Thickness of the edge
            s=100,  # Increase size of the dot for better visibility
        )

        # Get dynamically calculated offset
        x_offset, y_offset = get_label_offset(x, y, ax)

        # Add a smaller black arrow on top of the white one
        ax.annotate(
            label,
            xy=(x, y),  # The point to annotate
            xytext=(x + x_offset, y + y_offset),  # Dynamic offset
            arrowprops=dict(
                facecolor="white",
                arrowstyle="wedge",
                connectionstyle="arc3,rad=0.3",
                shrinkB=7,
            ),
            bbox=dict(
                boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"
            ),  # Label box styling
            fontsize=10,
            color="black",  # Label text color
        )

    # Add labels and title
    ax.set_xlabel("Time")
    ax.set_ylabel("Performance")
    ax.set_title(title)
    ax.legend(loc="upper left")

    # Display the plot
    ax.grid(True)
    plt.tight_layout()

    # Save the plot as an SVG file
    plt.savefig(file_name, format="svg")
    print(f"Saved plot as {file_name}")

    plt.show()
