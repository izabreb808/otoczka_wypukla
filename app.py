from flask import Flask, render_template, request
import matplotlib
matplotlib.use("Agg")  # <- TO DODAJ!
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    points = []
    error = None
    if request.method == "POST":
        try:
            input_data = request.form["points"]  # np. "(1,1),(2,3),(4,2)"
            # Parsujemy ciąg znaków do listy krotek
            points = eval("[" + input_data + "]")
            assert all(isinstance(p, tuple) and len(p) == 2 for p in points)
        except:
            error = "Niepoprawny format danych. Użyj np. (1,1),(2,3),(4,2)"
            return render_template("index.html", error=error)

        print("Otrzymane punkty:", points)

        unused = list(points)   # Lista punktów nieużytych w obliczaniu otoczki wypukłej
        ch = []   # Lista punktów otoczki wypukłej

        start_point = max(points, key=lambda p: (p[0], p[1]))  # Punkt startowy
        ch.append(start_point)
        unused.remove(start_point)

        # Funkcja wyznaczająca, po której stronie prostej stworzonej z dwóch punktów znajduje się reszta punktów (" < 0 " - punkty po lewej stronie, " == 0" - punkty na prostej, " > 0 " - punkty po prawej stronie)
        def on_right(p1, p2, p3):
            return (p3[0] - p2[0])*(p1[1] - p2[1]) - (p1[0] - p2[0])*(p3[1] - p2[1])

        # Funkcja obliczająca odległość dwóch punktów
        def distance(p1, p2):
            return (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2

        current_point = start_point
        while True:
            next_point = points[0]
            for p in points[1:]:
                if (on_right(p, current_point, next_point) > 0 or
                    (on_right(p, current_point, next_point) == 0 and distance(current_point, p) > distance(current_point, next_point))):
                    next_point = p

            if next_point == start_point:
                break
            ch.append(next_point)
            current_point = next_point

        # Komunikat tekstowy do wyświetlenia w HTML
        if len(ch) == 4:
            message = "Otoczka wypukła jest czworokątem."
        elif len(ch) == 3:
            message = "Otoczka wypukła jest trójkątem."
        elif len(ch) == 2:
            message = "Otoczka wypukła jest prostą."
        else:
            message = "Otoczka wypukła jest punktem."

        # Skrypt wyświetlający układ współrzędnych z punktami oraz otoczką wypukłą

        # Ekstrakcja koordynatów do wykresu
        x_coords_points = [point[0] for point in points]
        y_coords_points = [point[1] for point in points]

        x_coords_ch = [point[0] for point in ch]
        y_coords_ch = [point[1] for point in ch]

       # Stworzenie wykresu
        plt.figure(figsize=(8, 6))
        plt.scatter(x_coords_points, y_coords_points, label='Punkty', color='blue')
        plt.plot(x_coords_ch + [x_coords_ch[0]], y_coords_ch + [y_coords_ch[0]], label='Otoczka wypukła', color='red')  # Obwód otoczki wypukłej

        # Opis osi
        plt.xlabel('X-axis')
        plt.ylabel('Y-axis')
        plt.grid(True)
        plt.legend()

        plot_path = os.path.join("static", "plot.png")
        plt.savefig(plot_path)
        plt.close()

        return render_template("index.html", image="plot.png", message=message, points=points, convex_hull=ch)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)


# pip install flask matplotlib
# python app.py
# Otwórz przeglądarkę i wejdź na http://localhost:5000