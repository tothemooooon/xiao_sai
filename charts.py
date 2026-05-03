import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

matplotlib.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
matplotlib.rcParams["axes.unicode_minus"] = False

df = pd.read_csv("E:/code/model/process_data/q1_result.csv")

main_board = df[df["板块"] == "主板"].copy()
cy_board = df[df["板块"] == "创业板"].copy()

main_board = main_board.sort_index(ascending=False)
cy_board = cy_board.sort_index(ascending=False)

fig1, ax1 = plt.subplots(figsize=(10, 8))
colors1 = ["#1f77b4"] * len(main_board)
y_pos1 = range(len(main_board))
bars1 = ax1.barh(y_pos1, main_board["概率(%)"].values, color=colors1, height=0.7)

ax1.set_yticks(y_pos1)
ax1.set_yticklabels(main_board["涨幅区间"].values)
ax1.set_xlabel("概率(%)", fontsize=12)
ax1.set_title("主板个股涨停次交易日走势分布(%)", fontsize=14, fontweight="bold")
ax1.set_xlim(0, 65)

for i, (bar, val) in enumerate(zip(bars1, main_board["概率(%)"].values)):
    ax1.text(
        val + 0.5,
        bar.get_y() + bar.get_height() / 2,
        f"{val:.2f}%",
        va="center",
        fontsize=10,
    )

plt.tight_layout()
plt.savefig(
    "E:/code/model/results/question1_main_board.png", dpi=150, bbox_inches="tight"
)
plt.close()

fig2, ax2 = plt.subplots(figsize=(10, 8))
colors2 = ["#ff7f0e"] * len(cy_board)
y_pos2 = range(len(cy_board))
bars2 = ax2.barh(y_pos2, cy_board["概率(%)"].values, color=colors2, height=0.7)

ax2.set_yticks(y_pos2)
ax2.set_yticklabels(cy_board["涨幅区间"].values)
ax2.set_xlabel("概率(%)", fontsize=12)
ax2.set_title(
    "创业板/科创版个股涨停次交易日走势分布(%)", fontsize=14, fontweight="bold"
)
ax2.set_xlim(0, 65)

for i, (bar, val) in enumerate(zip(bars2, cy_board["概率(%)"].values)):
    ax2.text(
        val + 0.5,
        bar.get_y() + bar.get_height() / 2,
        f"{val:.2f}%",
        va="center",
        fontsize=10,
    )

plt.tight_layout()
plt.savefig("E:/code/model/results/question1_cyboard.png", dpi=150, bbox_inches="tight")
plt.close()

print("Charts saved successfully!")
print(f"Main board: question1_main_board.png")
print(f"Cy/Growth board: question1_cyboard.png")
