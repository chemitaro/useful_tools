import { ts_mock_a_1 } from '@/ts_mock/ts_mock_a/ts_mock_a_1';
import { ts_mock_b_1 } from '@/ts_mock/ts_mock_b/ts_mock_b_1';

export const ts_mock_1 = 'ts_mock_1';
console.log(ts_mock_a_1);
console.log(ts_mock_b_1);

interface Point {
  x: number;
  y: number;
}

function generateRandomPoint(): Point {
  return {
    x: Math.random(),
    y: Math.random(),
  };
}

const points: Point[] = [];

for (let i = 0; i < 5; i++) {
  points.push(generateRandomPoint());
}

console.log(points);

interface Shape {
  name: string;
  area(): number;
}

class Circle implements Shape {
  radius: number;

  constructor(radius: number) {
    this.radius = radius;
  }
  name: string;

  area(): number {
    return Math.PI * this.radius * this.radius;
  }
}

class Square implements Shape {
  sideLength: number;

  constructor(sideLength: number) {
    this.sideLength = sideLength;
  }
  name: string;

  area(): number {
    return this.sideLength * this.sideLength;
  }
}

const shapes: Shape[] = [];

shapes.push(new Circle(5));
shapes.push(new Square(10));

for (const shape of shapes) {
  console.log(`${shape.name}: ${shape.area()}`);
}
