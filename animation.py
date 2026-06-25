import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# Fixing random state for reproducibility
np.random.seed(19680801)

# Tweakable Parameters
amplitude = 1.0
frequency = 10.0
speed_interval_ms = 50 # Milliseconds between frames
num_frames = 200 # Total number of frames for the animation


def update(frame_number):
    xdata.append(frame_number)
    ydata.append(amplitude * np.sin(frame_number / frequency))
    line.set_data(xdata, ydata)
    ax.relim()
    ax.autoscale_view()
    return line,

fig, ax = plt.subplots()
xdata, ydata = [], []
line, = ax.plot([], [], 'r-')

ax.set_xlim(0, num_frames) # Adjust x-limit based on num_frames
ax.set_ylim(-amplitude * 1.5, amplitude * 1.5) # Adjust y-limit based on amplitude
ax.grid()

ani = animation.FuncAnimation(fig, update, frames=range(num_frames), blit=True, interval=speed_interval_ms)

# To save the animation, uncomment the following lines:
# Writer = animation.writers['ffmpeg']
# writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)
# ani.save('sine_wave.mp4', writer=writer)

# Save the animation as a GIF file
ani.save('animation.gif', writer='pillow', fps=20)
