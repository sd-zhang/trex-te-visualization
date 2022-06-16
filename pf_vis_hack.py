import csv

out_data = list()

with open("data/powerflow_series.csv") as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    header = next(reader)
    for row in reader:
        for idx in range(1, len(row)):
            time = row[0]
            size = float(row[idx])
            header_col = header[idx]
            if size >= 0:
                _, from_node, to_node = header_col.split('r')
            else:
                _, to_node, from_node = header_col.split('r')
                size = -size
            out_data.append({
                'time': int(time),
                'from': int(from_node),
                'to': int(to_node),
                'size': size
            })

with open('flows.csv', 'w', newline='') as csvfile:
    fieldnames = ['time', 'from', 'to', 'size']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in out_data:
        writer.writerow(row)