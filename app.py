from flask import Flask, render_template, request, jsonify
import os
import json
import re

app = Flask(__name__)


def contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def detect_features(text: str) -> dict:
    lowered = text.lower()

    genres = []
    tags = []
    mechanics = []
    strengths = []
    weaknesses = []
    recommendations = []
    score = 5

    # Жанры
    if contains_any(lowered, ["рогалик", "roguelike", "rogue-lite", "roguelite"]):
        genres.append("roguelike")
        score += 1
        strengths.append("жанр рогалика хорошо подходит для высокой реиграбельности")
        weaknesses.append("жанр требует аккуратного баланса случайности и прогрессии")
        recommendations.append("важно определить, что делает каждый забег уникальным")
        mechanics.extend([
            "процедурная генерация",
            "серия коротких забегов",
            "мета-прогрессия между попытками"
        ])

    if contains_any(lowered, ["выживание", "survival"]):
        genres.append("survival")
        score += 1
        strengths.append("механика выживания создаёт постоянное напряжение")
        weaknesses.append("есть риск превратить игру в однообразный сбор ресурсов")
        recommendations.append("нужно сбалансировать дефицит ресурсов и темп давления на игрока")
        mechanics.extend([
            "сбор ресурсов",
            "контроль здоровья или энергии",
            "давление окружения"
        ])

    if contains_any(lowered, ["хоррор", "ужас", "страш", "horror"]):
        genres.append("horror")
        score += 1
        strengths.append("у идеи есть потенциал сильной атмосферы и эмоционального воздействия")
        weaknesses.append("хоррор сложно удерживать только за счёт скримеров")
        recommendations.append("лучше делать упор на атмосферу, неизвестность и ограниченность информации")
        mechanics.extend([
            "ограниченная видимость",
            "звуковые триггеры",
            "атмосферное исследование"
        ])

    if contains_any(lowered, ["стратег", "strategy", "tower defense", "башн"]):
        genres.append("strategy")
        score += 1
        strengths.append("стратегические элементы увеличивают глубину принятия решений")
        weaknesses.append("избыточная сложность может отпугнуть игрока на старте")
        recommendations.append("стоит постепенно раскрывать механики через ранние игровые ситуации")
        mechanics.extend([
            "управление ресурсами",
            "тактический выбор",
            "планирование действий"
        ])

    if contains_any(lowered, ["платформер", "platformer", "прыж"]):
        genres.append("platformer")
        score += 1
        strengths.append("платформер хорошо подходит для быстрого и понятного игрового цикла")
        weaknesses.append("жанру трудно выделиться без сильной уникальной механики")
        recommendations.append("нужно добавить центральную механику, которая меняет привычный платформинг")
        mechanics.extend([
            "точное перемещение",
            "ритм препятствий",
            "уровневый челлендж"
        ])

    if contains_any(lowered, ["головолом", "puzzle", "пазл"]):
        genres.append("puzzle")
        score += 1
        strengths.append("головоломки хорошо работают, если у игры есть чёткое и читаемое правило")
        weaknesses.append("однообразные задачи быстро снижают интерес")
        recommendations.append("нужно строить усложнение через новые комбинации уже известных правил")
        mechanics.extend([
            "логические взаимодействия",
            "постепенное усложнение правил",
            "обучение через уровень"
        ])

    if contains_any(lowered, ["симулятор", "simulator", "тайкун", "tycoon"]):
        genres.append("simulation")
        score += 1
        strengths.append("симуляционные элементы хорошо удерживают игроков за счёт ощущения контроля и роста")
        weaknesses.append("симулятор может превратиться в набор скучных рутинных действий")
        recommendations.append("важно добавить интересные решения, а не только повторяющиеся действия")
        mechanics.extend([
            "управление системой",
            "рост показателей",
            "экономические решения"
        ])

    # Дополнительные особенности
    if contains_any(lowered, ["кооп", "coop", "co-op", "совместн"]):
        tags.append("co-op")
        score += 1
        strengths.append("кооператив усиливает социальную ценность проекта")
        weaknesses.append("кооператив увеличивает сложность тестирования и балансировки")
        recommendations.append("нужно решить, какие действия игроки выполняют вместе, а какие по отдельности")
        mechanics.extend([
            "совместное прохождение",
            "распределение ролей"
        ])

    if contains_any(lowered, ["pvp", "мультиплеер", "соревнов", "онлайн"]):
        tags.append("multiplayer")
        score += 1
        strengths.append("соревновательные элементы могут повысить вовлечённость игроков")
        weaknesses.append("сетевые режимы сильно усложняют разработку и баланс")
        recommendations.append("для прототипа лучше сначала проверить основную механику без сложной сетевой логики")
        mechanics.extend([
            "соревновательное взаимодействие",
            "балансировка ролей или билдов"
        ])

    if contains_any(lowered, ["база", "строить", "строительство", "постройка", "укреплен"]):
        tags.append("base-building")
        score += 1
        strengths.append("строительство базы усиливает ощущение прогресса и контроля над пространством")
        weaknesses.append("строительство может конфликтовать с быстрым темпом экшен-игры")
        recommendations.append("важно определить, когда игрок строит, а когда активно сражается или исследует")
        mechanics.extend([
            "строительство базы",
            "улучшение сооружений",
            "оборона точки"
        ])

    if contains_any(lowered, ["карточ", "deck", "card", "колод"]):
        tags.append("card-system")
        score += 1
        strengths.append("карточные элементы могут сделать билды разнообразными")
        weaknesses.append("карточная система требует очень аккуратного баланса")
        recommendations.append("стоит ограничить количество эффектов на раннем этапе прототипирования")
        mechanics.extend([
            "колода карт",
            "синергии эффектов",
            "выбор билдов"
        ])

    if contains_any(lowered, ["сюжет", "история", "диалог", "персонаж"]):
        tags.append("narrative")
        score += 1
        strengths.append("сюжетные элементы повышают эмоциональную вовлечённость")
        weaknesses.append("сюжет легко провисает, если не связан с игровыми действиями")
        recommendations.append("лучше интегрировать подачу истории в игровой процесс, а не только в текст")
        mechanics.extend([
            "нарративные события",
            "диалоги или выборы"
        ])

    if contains_any(lowered, ["процедур", "рандом", "случайн"]):
        tags.append("procedural")
        score += 1
        strengths.append("процедурность увеличивает вариативность прохождений")
        weaknesses.append("случайная генерация может создавать нечестные или скучные ситуации")
        recommendations.append("нужно контролировать диапазоны генерации и тестировать повторяемость качества")
        mechanics.extend([
            "процедурная генерация уровней или событий"
        ])

    if contains_any(lowered, ["мобил", "телефон", "android", "ios"]):
        tags.append("mobile")
        weaknesses.append("мобильная платформа требует особенно простого и удобного управления")
        recommendations.append("следует упростить интерфейс и ограничить количество действий на экране")
        mechanics.extend([
            "короткие игровые сессии",
            "упрощённое управление"
        ])

    if contains_any(lowered, ["2d", "2д", "пиксель", "pixel"]):
        strengths.append("2D-формат хорошо подходит для быстрого прототипирования и инди-разработки")

    if contains_any(lowered, ["3d", "3д"]):
        weaknesses.append("3D-разработка увеличивает объём работы по графике, анимации и окружению")
        recommendations.append("для MVP стоит сократить количество контента и сосредоточиться на одном ядре геймплея")

    # Общие эвристики по качеству описания
    word_count = len(re.findall(r"\w+", lowered))

    if word_count >= 18:
        score += 1
        strengths.append("идея описана достаточно подробно для первичного анализа")
    else:
        weaknesses.append("идея описана слишком кратко, из-за чего часть решений остаётся неопределённой")
        recommendations.append("полезно отдельно описать цель игрока, цикл игры и источник интереса")

    if word_count <= 6:
        score -= 1

    # Если идея выглядит как смесь нескольких систем — плюс за потенциал, но предупреждение за сложность
    complexity_markers = 0
    for marker_keywords in [
        ["рогалик", "roguelike", "roguelite"],
        ["выживание", "survival"],
        ["база", "строить", "строительство"],
        ["кооп", "coop", "совместн"],
        ["карточ", "deck", "card"],
        ["сюжет", "история", "диалог"],
        ["процедур", "рандом"]
    ]:
        if contains_any(lowered, marker_keywords):
            complexity_markers += 1

    if complexity_markers >= 3:
        score += 1
        strengths.append("в идее чувствуется потенциал глубокой системы и комбинирования механик")
        weaknesses.append("комбинация нескольких подсистем может сильно усложнить реализацию")
        recommendations.append("на первом этапе лучше выделить минимально жизнеспособную версию игрового цикла")

    # Базовые значения, если идея слишком общая
    if not genres:
        genres.append("indie concept")
        recommendations.append("стоит точнее определить жанр и ожидаемый игровой опыт")

    if not mechanics:
        mechanics.extend([
            "основной игровой цикл",
            "система прогрессии",
            "взаимодействие с окружением"
        ])

    if not strengths:
        strengths.append("идея имеет потенциал для быстрого прототипирования")

    if not weaknesses:
        weaknesses.append("в описании пока недостаточно деталей для точной оценки рисков")

    if not recommendations:
        recommendations.append("нужно уточнить уникальную механику и целевой игровой опыт")

    # Убираем повторы, сохраняя порядок
    def unique_keep_order(items: list[str]) -> list[str]:
        seen = set()
        result = []
        for item in items:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result

    genres = unique_keep_order(genres)
    tags = unique_keep_order(tags)
    mechanics = unique_keep_order(mechanics)
    strengths = unique_keep_order(strengths)
    weaknesses = unique_keep_order(weaknesses)
    recommendations = unique_keep_order(recommendations)

    score = max(4, min(score, 10))

    return {
        "genres": genres,
        "tags": tags,
        "core_mechanics": mechanics[:6],
        "strengths": strengths[:4],
        "weaknesses": weaknesses[:4],
        "recommendations": recommendations[:4],
        "score": f"{score}/10"
    }


def build_refined_idea(original_idea: str, features: dict) -> str:
    genres = ", ".join(features["genres"])
    tags = ", ".join(features["tags"]) if features["tags"] else "без дополнительных поджанровых тегов"

    return (
        f"Это игровая концепция в направлении {genres}, "
        f"в которой прослеживаются элементы {tags}. "
        f"Идея может быть усилена за счёт более чёткого определения основного игрового цикла, "
        f"мотивации игрока и уникальной механики, отличающей проект от аналогов."
    )


def local_analysis(idea: str) -> dict:
    features = detect_features(idea)

    return {
        "refined_idea": build_refined_idea(idea, features),
        "genre": ", ".join(features["genres"]),
        "core_mechanics": features["core_mechanics"],
        "strengths": features["strengths"],
        "weaknesses": features["weaknesses"],
        "recommendations": features["recommendations"],
        "score": features["score"]
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True)

    if not data or "idea" not in data:
        return jsonify({"error": "Некорректный запрос"}), 400

    idea = data["idea"].strip()

    if not idea:
        return jsonify({"error": "Введите описание игровой идеи"}), 400

    if len(idea) < 15:
        return jsonify({"error": "Описание слишком короткое. Добавьте больше деталей."}), 400

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return jsonify(local_analysis(idea))

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        prompt = f"""
Ты — ассистент по геймдизайну. Проанализируй игровую идею и верни только JSON.
Поля:
refined_idea, genre, core_mechanics, strengths, weaknesses, recommendations, score

Требования:
- core_mechanics, strengths, weaknesses, recommendations — массивы строк
- score — строка вида "8/10"
- ответ строго в JSON без пояснений

Игровая идея:
{idea}
"""

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Ты анализируешь игровые идеи и отвечаешь строго JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7
        )

        content = response.choices[0].message.content.strip()
        parsed = json.loads(content)
        return jsonify(parsed)

    except Exception as e:
        return jsonify({
            "error": "Не удалось выполнить анализ через LLM",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3000, debug=True)