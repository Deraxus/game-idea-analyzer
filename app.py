from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


GENRE_KEYWORDS = {
    "roguelike": ["рогалик", "roguelike", "rogue-like", "roguelite", "rogue-lite"],
    "survival": ["выживание", "survival"],
    "strategy": ["стратегия", "strategy", "tactical", "тактика", "тактическая"],
    "shooter": ["шутер", "shooter", "fps", "стрелялка"],
    "rpg": ["rpg", "рпг", "ролевая"],
    "platformer": ["платформер", "platformer"],
    "horror": ["хоррор", "ужасы", "horror"],
    "simulation": ["симулятор", "simulation"],
    "sandbox": ["песочница", "sandbox"],
}

MECHANIC_KEYWORDS = {
    "бой": ["стрелять", "стрельба", "бой", "сражаться", "атаковать", "враги", "убивать"],
    "исследование": ["исследовать", "исследование", "изучать", "искать", "эксплоринг"],
    "строительство": ["строить", "постройка", "база", "билдить", "укреплять"],
    "сбор ресурсов": ["ресурсы", "добыча", "собирать", "лут", "крафт-ресурсы"],
    "управление ресурсами": ["менеджмент", "управление", "экономика", "ресурсы", "распределять"],
    "прокачка": ["прокачка", "улучшения", "развитие", "навыки", "перки"],
    "выживание": ["выжить", "голод", "жажда", "опасность", "волны врагов"],
    "головоломки": ["головоломка", "загадки", "решать задачи", "пазл"],
}

GOAL_KEYWORDS = [
    "выжить",
    "победить",
    "уничтожить",
    "спасти",
    "дойти",
    "сбежать",
    "защитить",
    "построить",
    "развить",
]


def find_matches(text: str, keyword_map: dict) -> list:
    found = []

    for category, keywords in keyword_map.items():
        for keyword in keywords:
            if keyword in text:
                found.append(category)
                break

    return found


def detect_goal(text: str) -> str | None:
    for keyword in GOAL_KEYWORDS:
        if keyword in text:
            return f"Обнаружена предполагаемая игровая цель: «{keyword}»."
    return None


def evaluate_completeness(text: str, genres: list, mechanics: list, goal: str | None) -> tuple[str, int]:
    score = 0

    if len(text.split()) >= 8:
        score += 1
    if genres:
        score += 1
    if mechanics:
        score += 1
    if goal:
        score += 1

    if score <= 1:
        return "Описание недостаточно полное.", 2
    if score == 2:
        return "Описание частично раскрывает идею, но требует уточнений.", 5
    if score == 3:
        return "Описание в целом понятное и достаточно информативное.", 7
    return "Описание является достаточно полным для первичного анализа.", 9


def generate_strengths(genres: list, mechanics: list, text: str) -> list:
    strengths = []

    if len(mechanics) >= 2:
        strengths.append("Идея содержит сочетание нескольких игровых механик.")
    if "выживание" in mechanics or "survival" in genres:
        strengths.append("Концепция может обеспечивать напряжение и вовлечение игрока.")
    if "roguelike" in genres:
        strengths.append("Рогалик-структура может повысить реиграбельность.")
    if "прокачка" in mechanics:
        strengths.append("Наличие прогрессии повышает мотивацию игрока.")
    if len(text.split()) >= 15:
        strengths.append("Пользователь описал идею достаточно развернуто.")

    if not strengths:
        strengths.append("Идея сформулирована кратко и может служить основой для дальнейшей доработки.")

    return strengths


def generate_weaknesses(genres: list, mechanics: list, text: str) -> list:
    weaknesses = []

    if len(text.split()) < 8:
        weaknesses.append("Описание слишком краткое для уверенного анализа.")
    if not genres:
        weaknesses.append("Жанр игры не определён явно.")
    if not mechanics:
        weaknesses.append("Игровые механики раскрыты недостаточно.")
    if len(mechanics) >= 5:
        weaknesses.append("Идея может быть перегружена механиками для небольшого прототипа.")
    if "шутер" in text and "зомби" in text:
        weaknesses.append("Концепция может восприниматься как недостаточно оригинальная.")
    if not any(word in text for word in GOAL_KEYWORDS):
        weaknesses.append("Игровая цель не сформулирована явно.")

    if not weaknesses:
        weaknesses.append("Существенные слабые стороны не выявлены на базовом уровне анализа.")

    return weaknesses


def generate_recommendations(genres: list, mechanics: list, goal: str | None, text: str) -> list:
    recommendations = []

    if not genres:
        recommendations.append("Следует явно указать жанр игры.")
    if not mechanics:
        recommendations.append("Следует подробнее описать основные действия игрока.")
    if not goal:
        recommendations.append("Следует уточнить основную цель игрока.")
    if len(text.split()) < 12:
        recommendations.append("Желательно расширить описание идеи и добавить детали core loop.")
    if len(mechanics) >= 5:
        recommendations.append("Рекомендуется сократить количество механик и сфокусироваться на ключевой.")
    if "уник" not in text and "особен" not in text:
        recommendations.append("Следует добавить или подчеркнуть уникальную особенность проекта.")

    if not recommendations:
        recommendations.append("Идея уже подходит для дальнейшей детализации и перехода к проектированию механик.")

    return recommendations


def calculate_score(genres: list, mechanics: list, goal: str | None, text: str) -> int:
    score = 0

    if len(text.split()) >= 8:
        score += 2
    if genres:
        score += 2
    if mechanics:
        score += 2
    if goal:
        score += 2
    if len(mechanics) >= 2:
        score += 1
    if len(text.split()) >= 15:
        score += 1

    return max(1, min(score, 10))


def analyze_game_idea(idea_text: str) -> dict:
    normalized_text = idea_text.lower().strip()

    genres = find_matches(normalized_text, GENRE_KEYWORDS)
    mechanics = find_matches(normalized_text, MECHANIC_KEYWORDS)
    goal = detect_goal(normalized_text)

    completeness_text, _ = evaluate_completeness(normalized_text, genres, mechanics, goal)
    strengths = generate_strengths(genres, mechanics, normalized_text)
    weaknesses = generate_weaknesses(genres, mechanics, normalized_text)
    recommendations = generate_recommendations(genres, mechanics, goal, normalized_text)
    score = calculate_score(genres, mechanics, goal, normalized_text)

    return {
        "genre": genres if genres else ["не определён"],
        "mechanics": mechanics if mechanics else ["не определены"],
        "goal_analysis": goal if goal else "Игровая цель не определена явно.",
        "strengths": strengths,
        "weaknesses": weaknesses,
        "completeness": completeness_text,
        "recommendations": recommendations,
        "score": f"{score}/10"
    }


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()

        if data is None:
            return jsonify({"error": "Тело запроса должно быть в формате JSON."}), 400

        idea = data.get("idea", "").strip()

        if not idea:
            return jsonify({"error": "Поле 'idea' не должно быть пустым."}), 400

        if len(idea) < 5:
            return jsonify({"error": "Описание идеи слишком короткое для анализа."}), 400

        result = analyze_game_idea(idea)
        return jsonify(result), 200

    except Exception as error:
        return jsonify({
            "error": "Внутренняя ошибка сервера.",
            "details": str(error)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)