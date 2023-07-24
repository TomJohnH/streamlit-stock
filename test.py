import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set the style to match The Economist style
plt.style.use('bmh')

# Create some data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Create a figure and a set of subplots
fig, ax = plt.subplots()

# Plot the data
ax.plot(x, y, color='#EC111A')  # Economist red

# Set the title and labels
ax.set_title('Example Chart', fontsize=14, fontweight='bold', color='black', loc='left', pad=20)
ax.set_xlabel('X Axis', fontsize=12, fontweight='bold', color='black')
ax.set_ylabel('Y Axis', fontsize=12, fontweight='bold', color='black')

# Set the grid
ax.grid(True, which='both', color='black', linewidth=1, alpha=0.1)

# Set the spines
ax.spines['left'].set_color('black')
ax.spines['left'].set_linewidth(1)
ax.spines['bottom'].set_color('black')
ax.spines['bottom'].set_linewidth(1)

# Show the plot
plt.show()