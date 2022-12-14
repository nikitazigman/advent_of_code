import os
import re
import time
from pathlib import Path
from threading import Thread

CAVE_TYPE = list[list[str]]


def get_data(file_path: Path) -> str:
    data: str
    with open(file_path, "r") as f:
        data = f.read()

    return data


class Cave:
    sand_source = (0, 500)

    def __init__(self, data: str) -> None:
        self.x_min, self.y_min, self.x_max, self.y_max = self.get_edge_dots(data)
        self._cave: CAVE_TYPE

        self._cave = self.generate_empty_cave(
            self.x_max - self.x_min, self.y_max - self.y_min
        )
        self.draw_cave_map(data)
        self.frame = 0
        self.rendering = True

    def draw_cave_map(self, data: str) -> None:
        self.draw_sand_source()
        for line in data.split("\n"):
            self.draw_line(line)

        self._cave.append([" " for _ in range(self.x_max + 1)])
        self._cave.append(["#" for _ in range(self.x_max + 1)])

    def draw_sand_source(self) -> None:
        self._cave[self.sand_source[0] - self.y_min][
            self.sand_source[1] - self.x_min
        ] = "+"

    def draw_line(self, line: str) -> None:
        dots = [
            [int(i) for i in raw_dot.split(",")]
            for raw_dot in re.findall(r"\d+,\d+", line)
        ]

        for dot_idx in range(1, len(dots)):
            current_x, old_x = dots[dot_idx][0], dots[dot_idx - 1][0]
            current_y, old_y = dots[dot_idx][1], dots[dot_idx - 1][1]
            dif_x = current_x - old_x
            dif_y = current_y - old_y

            x_iter = range(dif_x) if dif_x >= 0 else range(dif_x, 1)
            for x in x_iter:
                x_coord = x + old_x - self.x_min
                y_coord = current_y - self.y_min
                self._cave[y_coord][x_coord] = "#"

            y_iter = range(dif_y + 1) if dif_y >= 0 else range(dif_y, 0)
            for y in y_iter:
                x_coord = current_x - self.x_min
                y_coord = y + old_y - self.y_min
                self._cave[y_coord][x_coord] = "#"

    def get_edge_dots(self, data: str) -> tuple[int, int, int, int]:
        max_y = 0
        for dot in re.findall(r"\d+,\d+", data):
            _, y = [int(i) for i in dot.split(",")]
            max_y = max(max_y, y)

        return 0, 0, self.sand_source[1] * 2, max_y

    @staticmethod
    def generate_empty_cave(x_length: int, y_length: int) -> list[list[str]]:
        empty_cave = []
        for _ in range(y_length + 1):
            empty_cave.append([" " for _ in range(x_length + 1)])

        return empty_cave

    def render(self) -> None:
        while self.rendering:
            os.system("clear")  # nosec
            rows = []
            for line in self._cave:
                row = "".join([i for i in line[300:-300]])
                rows.append(row)

            image = "\n".join(rows)

            print(image)
            time.sleep(0.1)

    def get_next_coord(self, coord: tuple[int, int]) -> None | tuple[int, int]:
        if self._cave[coord[0] + 1][coord[1]] == " ":
            return coord[0] + 1, coord[1]

        if self._cave[coord[0] + 1][coord[1] - 1] == " ":
            return coord[0] + 1, coord[1] - 1

        if self._cave[coord[0] + 1][coord[1] + 1] == " ":
            return coord[0] + 1, coord[1] + 1

        return None

    def draw_dot(self, coord: tuple[int, int], symbol: str) -> None:
        self._cave[coord[0]][coord[1]] = symbol

    def start_game(self) -> None:
        render_thread = Thread(target=self.render)
        render_thread.start()
        try:
            while True:
                self.frame += 1
                current_piece_pose = self.sand_source
                old_piece_pose = current_piece_pose
                while True:
                    next_coord = self.get_next_coord(current_piece_pose)
                    if next_coord is None:
                        if current_piece_pose == self.sand_source:
                            raise ValueError
                        break
                    old_piece_pose = current_piece_pose
                    current_piece_pose = next_coord
                    self.draw_dot(old_piece_pose, " ")
                    self.draw_dot(current_piece_pose, "*")
                    time.sleep(0.00000001)

        except ValueError:
            self.rendering = False
            render_thread.join()
            return


if __name__ == "__main__":
    file = Path(__file__).resolve().parent.joinpath("input.txt")
    data = get_data(file)

    cave = Cave(data)
    cave.start_game()
    print(cave.frame)
