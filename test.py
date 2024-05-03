from sklearn.preprocessing import MultiLabelBinarizer

y = []
for i in range(1,17):
    y.append([i])

mlb = MultiLabelBinarizer()
y_bin = mlb.fit_transform(y)

print(y_bin)