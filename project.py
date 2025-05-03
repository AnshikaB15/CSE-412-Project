from flask import Flask, render_template, request, redirect, url_for, jsonify
import psycopg2

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        dbname="",
        user="",
        password="",
        host="localhost",
        port="8888"
    )

@app.route("/", methods=["GET", "POST"])
def index():
    country  = request.values.get("country")
    city     = request.values.get("city")
    category = request.values.get("category")
    uid      = request.values.get("user_id")

    if uid:
       
        pass

    if country and city and category:
        if category == "activities":
            return redirect(url_for("activities", country=country, city=city))
        elif category == "transportation":
            return redirect(url_for("transportation", country=country, city=city))
        elif category == "hotels":
            return redirect(url_for("hotels", country=country, city=city))

    return render_template("index.html")

@app.route("/activities")
def activities():
    country = request.args.get("country")
    city    = request.args.get("city")
    results = []

    if country and city:
        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute("""
            SELECT activity_id, name, price, duration_hr, age_limit
            FROM activities
            WHERE country_name = %s AND city_name = %s;
        """, (country, city))
        results = cur.fetchall()
        cur.close()
        conn.close()

    return render_template("activities.html", city_name=city, results=results)

@app.route("/transportation")
def transportation():
    city    = request.args.get("city")
    results = []

    if city:
        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute(
            """
            SELECT t.transport_id,
                   t.type,
                   t.cost
              FROM transportation AS t
              JOIN city           AS c ON t.city_id = c.city_id
             WHERE c.name = %s;
            """,
            (city,),
        )
        results = cur.fetchall()
        cur.close()
        conn.close()

    return render_template("transportation.html", city_name=city, results=results)


@app.route("/city")
def cities():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT c.name AS city_name,
           co.name AS country_name
    FROM city AS c
    JOIN country AS co ON c.country_id = co.country_id;
""")
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template("cities.html", results=results)


@app.route("/country")
def countries():
    results = []
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT name FROM country;")
    results = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("countries.html", results=results)



@app.route("/hotels")
def hotels():
    city    = request.args.get("city")
    results = []

    if city:
        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute(
            """
            SELECT h.hotel_id,
                   h.name,
                   h.star_rating,
                   h.price_per_night,
                   h.address
              FROM hotel AS h
              JOIN city  AS c ON h.city_id = c.city_id
             WHERE c.name = %s;
            """,
            (city,),
        )
        results = cur.fetchall()
        cur.close()
        conn.close()

    return render_template("hotels.html", city_name=city, results=results)


@app.route("/add_note", methods=["POST"])
def add_note():
    data = request.get_json()
    uid = data.get("uid")
    content = data.get("content")

    if not uid or not content:
        return jsonify({"error": "Missing uid or content"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    
    cur.execute("SELECT noteid FROM add_note WHERE uid = %s", (uid,))
    existing = cur.fetchone()

    if existing:
        
        cur.execute("UPDATE add_note SET content = %s WHERE uid = %s", (content, uid))
    else:
        
        cur.execute("INSERT INTO add_note (uid, content) VALUES (%s, %s)", (uid, content))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(debug=True)






