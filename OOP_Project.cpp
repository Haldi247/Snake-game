#include <iostream>
#include "raylib.h"
#include <deque>
#include <raymath.h>

const float cellSize = 20;
const float cellCount = 30;
const float offset = 72;
int screen_size = cellCount * cellSize;

Color l_pink = {247, 178, 216, 255};
Color pink = {254, 110, 148, 255};
Color d_pink = {222, 93, 131, 255};

double lastUpdateTime = 0;

bool eventTriggered(double interval)
{
    double currentTime = GetTime();
    if (currentTime - lastUpdateTime >= interval)
    {
        lastUpdateTime = currentTime;
        return true;
    }
    return false;
}

bool isSamePos(Vector2 element, std::deque<Vector2> snakebody)
{
    for (unsigned i = 0; i < snakebody.size(); i++)
    {
        if (Vector2Equals(element, snakebody[i]))
        {
            return true;
        }
    }
    return false;
}
class food
{
public:
    Vector2 position;
    Vector2 big_position;
    Texture2D texture;

    food(std::deque<Vector2> snakebody)
    {
        // Image image = LoadImage("project/Pixel.jpg");
        // Texture2D texture = LoadTexture("Pixel.png");
        // UnloadImage(image);
        position = randomPosition(snakebody);
    }
    ~food()
    {
        // UnloadTexture(texture);
    }
    void Draw()
    {
        // DrawTexture(texture, (position.x) * cellSize, (position.y) * cellSize, WHITE);
        DrawCircle((position.x) * cellSize + offset, (position.y) * cellSize + offset, cellSize / 2, l_pink);
    }
    Vector2 randomCell()
    {
        float x = GetRandomValue(2, cellCount - 2);
        float y = GetRandomValue(2, cellCount - 2);
        return Vector2{x, y};
    }
    Vector2 randomPosition(std::deque<Vector2> snakebody)
    {
        position = randomCell();
        while (isSamePos(position, snakebody) || Vector2Equals(position, big_position))
        {
            position = randomCell();
        }
        return position;
    }
};
class Snake
{
public:
    std::deque<Vector2> body = {Vector2{23, 25}, Vector2{24, 25}, Vector2{25, 25}};
    Vector2 direction = {-1, 0};
    bool addSegment = false;

    void Draw()
    {
        float x_0 = body[0].x;
        float y_0 = body[0].y;

        DrawCircle(x_0 * cellSize + offset, y_0 * cellSize + offset, cellSize / 2 + 4, d_pink);

        for (unsigned int i = 1; i < body.size(); i++)
        {
            float x = body[i].x;
            float y = body[i].y;
            DrawCircle(x * cellSize + offset, y * cellSize + offset, cellSize / 2 + 1, d_pink);
            // Rectangle segment= Rectangle{x*cellSize,y*cellSize+15,cellSize*2,cellSize*2};
            // DrawRectangleRounded(segment,0.5,6,d_pink);
        }
    }
    void Update()
    {
        body.push_front(Vector2Add(body[0], direction));
        if (addSegment)
        {
            addSegment = false;
        }
        else
            body.pop_back();
    }
    void Reset()
    {
        body = {Vector2{23, 25}, Vector2{24, 25}, Vector2{25, 25}};
        direction = {-1, 0};
    }
};
class Game
{
public:
    Snake snake = Snake();
    food f = food(snake.body);
    bool running = false;
    int fail = 0;
    int high_score = 0;
    double interval = 0.1;
    int pause = 1;

    void Draw()
    {
        f.Draw();;
        snake.Draw();
    }

    void Update()
    {
        if (running)
        {
            snake.Update();
            foodCollision();
            edgeCollision();
            tailCollision();
        }
    }
    void foodCollision()
    {
        if (Vector2Equals(snake.body[0], f.position))
        {
            f.position = f.randomPosition(snake.body);
            snake.addSegment = true;
        }
    }
    void edgeCollision()
    {
        if (snake.body[0].x == cellCount || snake.body[0].x == 0)
        {
            GameOver();
        }
        if (snake.body[0].y == cellCount || snake.body[0].y == 0)
        {
            GameOver();
        }
    }
    void tailCollision()
    {
        for (int i = 1; i < snake.body.size(); i++)
        {
            if (Vector2Equals(snake.body[0], snake.body[i]))
                GameOver();
        }
    }
    void GameOver()
    {
        snake.Reset();
        f.position = f.randomPosition(snake.body);
        running = false;
        fail++;
    }
    int Score()
    {
        return snake.body.size() - 3;
    }
    int highScore()
    {
        if (high_score < Score())
            high_score = Score();
        return high_score;
    }
    double speed()
    {

        if (Score() == 0)
            interval = 0.1;
        else if (Score() == 10)
            interval = 0.08;
        else if (Score() == 15)
            interval = 0.065;
        else if (Score() == 25)
            interval = 0.05;

        return interval;
    }
    void Controls()
    {
        if (IsKeyDown(KEY_UP) && snake.direction.y != 1)
        {
            snake.direction = {0, -1};
            running = true;
            //     if (eventTriggered(0.2))
            // {
            //     game.Update();
            // }
        }
        if (IsKeyDown(KEY_DOWN) && snake.direction.y != -1)
        {
            snake.direction = {0, 1};
            running = true;
            //     if (eventTriggered(0.2))
            // {
            //     game.Update();
            // }
        }
        if (IsKeyDown(KEY_RIGHT) && snake.direction.x != -1)
        {
            snake.direction = {1, 0};
            running = true;
            //      if (eventTriggered(0.2))
            // {
            //     game.Update();
            // }
        }
        if (IsKeyDown(KEY_LEFT) && snake.direction.x != 1)
        {
            snake.direction = {-1, 0};
            running = true;
            //      if (eventTriggered(0.2))
            // {
            //     game.Update();
            //
        }
        if (IsKeyPressed(KEY_SPACE))
        {
            pause++;
            fail = 0;
            if (pause % 2 == 1)
                running = false;
            else
                running = true;
        }
    }
};

int main()
{
    InitWindow(2 * offset + screen_size, 2 * offset + screen_size, "SNAKE GAME");
    SetTargetFPS(60);

    Game game = Game();

    while (!WindowShouldClose())
    {
        BeginDrawing();

        if (eventTriggered(game.speed()))
        {
            game.Update();
        }

        game.Controls();

        ClearBackground(BLACK);

        DrawRectangleLinesEx(Rectangle{offset + 3, offset + 3, cellSize * cellCount - 7, cellSize * cellCount - 7}, 2, WHITE);
        DrawText("SNAKE GAME", offset + 3, 40, 30, WHITE);
        DrawText(TextFormat("%i", game.Score()), offset + 3, cellCount * cellSize + offset + 3, 20, WHITE);
        DrawText("HIGH SCORE:", 400, cellCount * cellSize + offset + 3, 20, WHITE);
        DrawText(TextFormat("%i", game.highScore()), 535, cellCount * cellSize + offset + 3, 20, WHITE);

            if (!game.running)
            {
                if (game.fail == 0)
                    DrawText("START GAME", offset + 15, screen_size / 2, 83, WHITE);
                else
                    DrawText("GAME OVER", offset + 15, screen_size / 2, 94, WHITE);
            }

        game.Draw();
        EndDrawing();
    }

    CloseWindow();

    return 0;
}