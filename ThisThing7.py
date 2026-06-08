from PIL import Image, ImageDraw
import math
import os

COLOR_TO_TREE = {
    (204, 142, 105): "Generic",
    (234, 184, 146): "Oak",
    (163, 75, 75): "Cherry",
    (215, 197, 154): "Fir",
    (205, 205, 205): "Birch",
    (105, 64, 40): "Walnut",
    (143, 76, 42): "Koa",
    (255, 0, 0): "Volcano",
    (52, 142, 64): "GreenSwampy",
    (226, 155, 64): "GoldSwampy",
    (226, 220, 188): "Palm",
    (255, 255, 0): "SnowGlow",
    (159, 243, 233): "Frost",
    (16, 42, 220): "CaveCrawler",
    (159, 173, 192): "BlueSpruce",
    (248, 248, 248): "LoneCave",
    (170, 85, 0): "Spooky"
}

COLOR_PALETTE = list(COLOR_TO_TREE.keys())
TREE_TO_COLOR = {v: k for k, v in COLOR_TO_TREE.items()}

LUA_START = "local partTable = {\n"
LUA_END = """}

local previewFolder = workspace:FindFirstChild("Builds") or Instance.new("Folder", workspace)
previewFolder.Name = "Builds"

for _, v in pairs(partTable) do
    local part = game.ReplicatedStorage.ClientItemInfo:FindFirstChild(v.Name):FindFirstChildOfClass('Model'):Clone()
    part.Parent = previewFolder
    part:SetPrimaryPartCFrame(v.CFrame)
    part.Name = v.Name
    local treeValue = Instance.new("StringValue", part)
    treeValue.Name = "TreeValue"
    treeValue.Value = v.TreeValue

    if v.TreeValue == "Generic" then part.BuildDependentWood.Color = Color3.fromRGB(204, 142, 105) 
    elseif v.TreeValue == "Oak" then part.BuildDependentWood.Color = Color3.fromRGB(234, 184, 146) 
    elseif v.TreeValue == "Cherry" then part.BuildDependentWood.Color = Color3.fromRGB(163, 75, 75) 
    elseif v.TreeValue == "Fir" then part.BuildDependentWood.Color = Color3.fromRGB(215, 197, 154) 
    elseif v.TreeValue == "Birch" then part.BuildDependentWood.Color = Color3.fromRGB(205, 205, 205) 
    elseif v.TreeValue == "Walnut" then part.BuildDependentWood.Color = Color3.fromRGB(105, 64, 40) 
    elseif v.TreeValue == "Koa" then part.BuildDependentWood.Color = Color3.fromRGB(143, 76, 42) 
    elseif v.TreeValue == "Volcano" then part.BuildDependentWood.Color = Color3.fromRGB(255, 0, 0) 
    elseif v.TreeValue == "GreenSwampy" then part.BuildDependentWood.Color = Color3.fromRGB(52, 142, 64) 
    elseif v.TreeValue == "GoldSwampy" then part.BuildDependentWood.Color = Color3.fromRGB(226, 155, 64) 
    elseif v.TreeValue == "Palm" then part.BuildDependentWood.Color = Color3.fromRGB(226, 220, 188) 
    elseif v.TreeValue == "SnowGlow" then part.BuildDependentWood.Color = Color3.fromRGB(255, 255, 0) 
    elseif v.TreeValue == "Frost" then part.BuildDependentWood.Color = Color3.fromRGB(159, 243, 233) 
    elseif v.TreeValue == "CaveCrawler" then part.BuildDependentWood.Color = Color3.fromRGB(16, 42, 220) 
    elseif v.TreeValue == "BlueSpruce" then part.BuildDependentWood.Color = Color3.fromRGB(159, 173, 192) 
    elseif v.TreeValue == "LoneCave" then part.BuildDependentWood.Color = Color3.fromRGB(248, 248, 248) 
    elseif v.TreeValue == "Spooky" then 
        part.BuildDependentWood.Material = Enum.Material.Granite 
        part.BuildDependentWood.Color = Color3.fromRGB(170, 85, 0) 
    elseif v.TreeValue == "SpookyNeon" then 
        part.BuildDependentWood.Material = Enum.Material.Neon 
        part.BuildDependentWood.Color = Color3.fromRGB(170, 85, 0) 
    end

    for _, _Part in pairs(part:GetChildren()) do
        if _Part:IsA('BasePart') and _Part.Transparency == 0 then
            _Part.Transparency = 0.3
        end
    end
end
"""

# ─────────────────────────────────────────────────────────────────────────────
# РЕЖИМ 1 — Минимум блоков (полы в приоритете для больших квадратных зон)
# Floor pieces cover large square areas first → fewer total blocks.
# Wall/Post pieces are still used wherever they fit better.
# ─────────────────────────────────────────────────────────────────────────────
BLOCK_TYPES_EFFICIENT = [
    # (ширина, высота, имя детали, матрица вращения CFrame)
    (8, 8, 'Floor1Large',   '0, 1, 0, 1, 0, 0, 0, 0, -1'),
    (8, 4, 'Wall2Tall',     '0, 0, 1, 1, 0, 0, 0, 1, 0'),       # 8x4 горизонт.
    (4, 8, 'Wall2Tall',     '0, 0, 1, 0, 1, 0, -1, 0, 0'),      # 4x8 верт.
    (8, 2, 'Wall2TallThin', '0, 0, -1, -1, 0, 0, 0, 1, 0'),     # 8x2 горизонт.
    (2, 8, 'Wall2TallThin', '0, 0, -1, 0, 1, 0, 1, 0, 0'),      # 2x8 верт.
    (4, 4, 'Floor1',        '0, 1, 0, 1, 0, 0, 0, 0, -1'),
    (4, 2, 'Wall2Short',    '0, 0, -1, 0, 1, 0, 1, 0, 0'),      # 4x2
    (2, 4, 'Wall2Thin',     '0, 0, -1, 0, 1, 0, 1, 0, 0'),      # 2x4
    (2, 2, 'Floor1Small',   '0, 1, 0, 1, 0, 0, 0, 0, -1'),
    (4, 1, 'Post',          '-1, 0, 0, 0, 0, 1, 0, 1, 0'),      # 4x1 горизонт.
    (1, 4, 'Post',          '-1, 0, 0, 0, 1, 0, 0, 0, -1'),     # 1x4 верт.
    (1, 1, 'Floor1Tiny',    '0, 1, 0, 1, 0, 0, 0, 0, -1')
]

# ─────────────────────────────────────────────────────────────────────────────
# РЕЖИМ 2 — Приоритет стеновых деталей (Wall2Tall, Wall2TallThin, Wall2Short,
#            Wall2Thin, Post используются везде, где могут поместиться)
# NOTE: больше блоков, зато чертежи стен/постов задействуются максимально.
# ─────────────────────────────────────────────────────────────────────────────
BLOCK_TYPES_WALL_PRIORITY = [
    # (ширина, высота, имя детали, матрица вращения CFrame)
    (8, 4, 'Wall2Tall',     '0, 0, 1, 1, 0, 0, 0, 1, 0'),       # 8x4 горизонт.
    (4, 8, 'Wall2Tall',     '0, 0, 1, 0, 1, 0, -1, 0, 0'),      # 4x8 верт.
    (8, 2, 'Wall2TallThin', '0, 0, -1, -1, 0, 0, 0, 1, 0'),     # 8x2 горизонт.
    (2, 8, 'Wall2TallThin', '0, 0, -1, 0, 1, 0, 1, 0, 0'),      # 2x8 верт.
    (4, 2, 'Wall2Short',    '0, 0, -1, 0, 1, 0, 1, 0, 0'),      # 4x2
    (2, 4, 'Wall2Thin',     '0, 0, -1, 0, 1, 0, 1, 0, 0'),      # 2x4
    (4, 1, 'Post',          '-1, 0, 0, 0, 0, 1, 0, 1, 0'),      # 4x1 горизонт.
    (1, 4, 'Post',          '-1, 0, 0, 0, 1, 0, 0, 0, -1'),     # 1x4 верт.
    # Полы — только как запасной вариант для зон, не покрытых стенами/постами
    (8, 8, 'Floor1Large',   '0, 1, 0, 1, 0, 0, 0, 0, -1'),
    (4, 4, 'Floor1',        '0, 1, 0, 1, 0, 0, 0, 0, -1'),
    (2, 2, 'Floor1Small',   '0, 1, 0, 1, 0, 0, 0, 0, -1'),
    (1, 1, 'Floor1Tiny',    '0, 1, 0, 1, 0, 0, 0, 0, -1')
]


def get_closest_color(pixel, palette):
    r1, g1, b1 = pixel[:3]
    min_distance = float('inf')
    closest_color = palette[0]
    for color in palette:
        r2, g2, b2 = color
        distance = math.sqrt((r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2)
        if distance < min_distance:
            min_distance = distance
            closest_color = color
    return closest_color


def process_image(input_path, output_name_prefix, save_mode, block_types):
    img = Image.open(input_path)
    img_width, img_height = 200, 200
    img = img.resize((img_width, img_height), Image.Resampling.LANCZOS).convert("RGBA")

    BASE_X = 167.0
    BASE_Y = 1.2
    BASE_Z = -97.0

    print("Преобразую пиксели в сетку материалов...")
    grid    = [[None  for _ in range(img_width)] for _ in range(img_height)]
    visited = [[False for _ in range(img_width)] for _ in range(img_height)]

    for y in range(img_height):
        for x in range(img_width):
            pixel = img.getpixel((x, y))
            if pixel[3] < 128:
                visited[y][x] = True   # прозрачный — пропускаем
            else:
                closest = get_closest_color(pixel, COLOR_PALETTE)
                grid[y][x] = COLOR_TO_TREE[closest]

    blocks_data = []

    wood_counts = {}
    blueprint_counts = {
        'Floor1Large':  0,
        'Wall2Tall':    0,
        'Wall2TallThin':0,
        'Floor1':       0,
        'Wall2Short':   0,
        'Wall2Thin':    0,
        'Floor1Small':  0,
        'Post':         0,
        'Floor1Tiny':   0
    }

    preview_img = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(preview_img)

    print("Оптимизация: Каскадный поиск блоков прямоугольных и квадратных форм...")

    for w, h, part_name, rot_matrix in block_types:
        for y in range(0, img_height - h + 1):
            for x in range(0, img_width - w + 1):
                if visited[y][x]:
                    continue

                match = True
                first_val = grid[y][x]

                for dy in range(h):
                    for dx in range(w):
                        if visited[y + dy][x + dx] or grid[y + dy][x + dx] != first_val:
                            match = False
                            break
                    if not match:
                        break

                if match:
                    for dy in range(h):
                        for dx in range(w):
                            visited[y + dy][x + dx] = True

                    block_color = TREE_TO_COLOR[first_val]
                    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=block_color + (255,))

                    block_z = BASE_Z - x - (w / 2.0)
                    block_y = BASE_Y + img_height - y - (h / 2.0) + 0.2

                    z_str = f"{block_z:.3f}"
                    y_str = f"{block_y:.3f}"
                    x_str = f"{BASE_X:.3f}"

                    cframe_str = f"CFrame.new({x_str}, {y_str}, {z_str}, {rot_matrix})"
                    line = f"    {{CFrame = {cframe_str}, Name = '{part_name}', TreeValue = '{first_val}'}},"
                    blocks_data.append(line)

                    wood_counts[first_val] = wood_counts.get(first_val, 0) + 1
                    blueprint_counts[part_name] += 1

    if not blocks_data:
        print("На картинке не найдено ни одного непрозрачного пикселя! Файлы не созданы.")
        return

    print(f"Всего объектов после сжатия: {len(blocks_data)}")

    # ── Сохранение скриптов ──────────────────────────────────────────────────
    CHUNK_SIZE = 5000

    if save_mode in ['2', '3']:
        single_filename = f"{output_name_prefix}_full.txt"
        with open(single_filename, "w", encoding="utf-8") as f:
            f.write(LUA_START)
            f.write("\n".join(blocks_data) + "\n")
            f.write(LUA_END)
        print(f"  -> Сохранен ЦЕЛЬНЫЙ скрипт: {single_filename}")

    if save_mode in ['1', '3']:
        total_chunks = math.ceil(len(blocks_data) / CHUNK_SIZE)
        print(f"Разбиваю скрипт. Количество частей: {total_chunks}")
        for i in range(total_chunks):
            chunk = blocks_data[i * CHUNK_SIZE : (i + 1) * CHUNK_SIZE]
            file_name = f"{output_name_prefix}.txt" if i == 0 else f"{output_name_prefix}({i}).txt"
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(LUA_START)
                f.write("\n".join(chunk) + "\n")
                f.write(LUA_END)
            print(f"  -> Сохранена часть: {file_name} ({len(chunk)} строк)")

    # ── Отчет по дереву и чертежам ───────────────────────────────────────────
    wood_filename = f"wood_{output_name_prefix}.txt"
    with open(wood_filename, "w", encoding="utf-8") as wf:
        wf.write(f"📊 Отчет по ресурсам для постройки '{output_name_prefix}'\n")
        wf.write("=" * 60 + "\n\n")

        wf.write("📝 НЕОБХОДИМЫЕ ЧЕРТЕЖИ (ДЕТАЛИ):\n")
        total_blueprints = 0
        for bp, count in blueprint_counts.items():
            if count > 0:
                wf.write(f"📐 {bp}: {count} шт.\n")
                total_blueprints += count
        wf.write(f"\nВсего деталей в конструкции: {total_blueprints} шт.\n")
        wf.write("-" * 60 + "\n\n")

        wf.write("🌳 НЕОБХОДИМОЕ ДЕРЕВО (КАЖДАЯ ДЕТАЛЬ = 1 КУСОК):\n")
        total_wood = 0
        for tree, count in sorted(wood_counts.items(), key=lambda item: item[1], reverse=True):
            wf.write(f"🌲 {tree}: {count} шт.\n")
            total_wood += count
        wf.write("\n" + "=" * 60 + "\n")
        wf.write(f"ИТОГО КУСКОВ ДЕРЕВА: {total_wood} шт.\n")

    print(f"📊 Отчет по чертежам и дереву успешно сохранен в {wood_filename}")

    # ── Превью ───────────────────────────────────────────────────────────────
    preview_filename = f"preview_{output_name_prefix}.png"
    preview_img.save(preview_filename)
    print(f"🖼️ Превью изображения успешно сохранено в {preview_filename}")


if __name__ == "__main__":
    print("Введи имя файла картинки (например, art.png):")
    input_img = input().strip()

    if not os.path.exists(input_img):
        print(f"Файл {input_img} не найден!")
    else:
        output_prefix = os.path.splitext(input_img)[0]

        print("\nКак сохранить lua-скрипты?")
        print("1 - Разбить на несколько мелких файлов (лучше для слабых пк)")
        print("2 - Сохранить одним огромным файлом")
        print("3 - И разбить, и создать один большой файл (оба варианта)")
        mode = input("Выбери (1/2/3): ").strip()
        if mode not in ['1', '2', '3']:
            mode = '1'

        print("\nКакой режим упаковки блоков?")
        print("1 - Минимум блоков   (Floor1Large/Floor1 покрывают большие зоны,")
        print("                      Wall/Post используются для прямоугольных остатков)")
        print("2 - Приоритет стен   (Wall2Tall, Wall2TallThin, Wall2Short, Wall2Thin,")
        print("                      Post используются везде, где помещаются;")
        print("                      Floor — только запасной вариант)")
        pack_mode = input("Выбери (1/2): ").strip()

        if pack_mode == '2':
            chosen_blocks = BLOCK_TYPES_WALL_PRIORITY
            print("→ Режим: приоритет стеновых деталей")
        else:
            chosen_blocks = BLOCK_TYPES_EFFICIENT
            print("→ Режим: минимальное количество блоков")

        process_image(input_img, output_prefix, mode, chosen_blocks)