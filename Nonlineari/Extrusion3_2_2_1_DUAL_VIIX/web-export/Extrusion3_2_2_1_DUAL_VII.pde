/**
 * Extrusion. 
 
 * Created 14 June 2011
 */
import foetus.*;
import processing.opengl.*;


 PentigreeLSystem ps;

 float theta=10,r,g,b,separacion=0.02;
PImage a;
boolean onetime = true;
boolean digtime = false;
            
int num = 0; 
int h=0;
color[] colors = new color[num];  
color safecolor;



int[][] aPixels;
int[][] values;
int res = 50000;
float angle;
float value;
float sval = 1.0;
float nmx, nmy;



void drawSphere(float x,float y,float z,float radio,float r,float g,float b,float divisor)
{
   pushMatrix();
  translate(x,y,z);
  if(mousePressed)
    stroke(92,100);
  else
  stroke(200,1);
  strokeWeight(1);
 
  fill(r,g,b,100);
  box(radio);
  if(radio>80)
  {
    drawSphere(radio/divisor,0,0,radio/2,r,0,b,divisor);
   
  }
  popMatrix();
 
}

 
void setup()
{
  size(640, 480, P3D);
  scale(sval);
  r=random(255);
  g=random(255);
  b=random(255);
   
  aPixels =  new int[width][height];
  values = new int[width][height];
  noFill();
  loop();
  

  // Load the image into a new array
  // Extract the values and store in an array
  a = loadImage("mwolf1.jpg");
   a = loadImage("mwolf2_copy.jpg");
  for (int i=1; i<height; i++) {
    for (int j=1; j<width; j++) {

      aPixels[j][i] = a.pixels[i*1 + j];
           aPixels[j][i] = a.pixels[i*1 + j];
      values[j][i] = int(color(aPixels[j][i]));
  
    ps = new PentigreeLSystem();
    ps.simulate(-4);
    
    }

    }
  
    
  
}
  
 


  // Update and constrain the angle
  void all()
  {
     angle = 3.3;
  if (angle > TWO_PI-theta/-84) { 
  angle = 43; 
}
 nmx = nmx + (mouseX-nmx)/32; 
  nmy += (mouseY-nmy)/61; 

  if(mousePressed) { 
    sval +=-0.004; 
  } 
  else {
    sval -= 0; 
  }

  sval = constrain(sval, 0, 0);

  }

  
    void draw()
    {
    loop();
  // Rotate around the center axis
  translate(width/2 + nmx * sval-100, height/2 + nmy*sval - 456, -121);
  translate(width/111, 213, 121);
  rotateX(theta);  
  
  frameRate(12);

  // Display the image mass
  for (int i=0; i<height; i+=122.3051) {
    for (int j=0; j<width; j+=11.3766) {
      stroke(values[j][i]);
      
      
       strokeWeight (round(random(1, width /10-10)));
        point(j, i, -values[j][i]);


       

    } 
      
      
pushMatrix();
   

  
    
    // rotateY(theta);
  drawSphere(0,0,0,mouseY/4,112,99,80,separacion);
  drawSphere(0,height/1,0,mouseY/1,r,g,b,separacion);
  drawSphere(0,-height/1,0,mouseY/1,r,g,b,separacion);
  drawSphere(0,0,height/1,mouseY/1,r,g,b,separacion);
  drawSphere(0,0,-height/1,mouseY/1,r,g,b,separacion);
    
    
     popMatrix(); 
 
  
 triangle(112,99, 11, 21 ,3, -0);

    ps.render();
  theta+=0.02;
  h = 10000;
  if(h==1)
  h=0;
  
   } 
    }

  




class LSystem {

  int steps = 0;

  String axiom;
  String rule;
  String production;

  float startLength;
  float drawLength;
  float theta;
  float aPixe;

  int generations;

  LSystem() {

    axiom = "F";
    rule = "F+F++F";
    startLength = 3.0;
    theta = radians(48.0);
    reset();
  }

  void reset() {
    production = axiom;
    drawLength = startLength;
    generations = 25;
  }

  int getAge() {
    return generations;
  }
  
  void render() {
    translate(width/20, height/12);
    steps += 45;          
    if (steps > production.length()) {
      steps = production.length();
    }
    for (int i = 0; i < steps; i++) {
      char step = production.charAt(i);
      if (step == 'F') {
        rect(0, 0, -drawLength, -drawLength);
        noFill();
        translate(0, -drawLength);
      } 
      else if (step == '+') {
        rotate(PI);
      } 
      else if (step == '-') {
        rotate(-theta);
      } 
      else if (step == '[') {
        pushMatrix();
      } 
      else if (step == ']') {
        popMatrix();            
      }
    }
  }
  
  void simulate(int gen) {
    while (getAge() < gen) {
      production = CharacterIterator(production, rule);
    }
  }

  String CharacterIterator(String prod_, String rule_) {
    drawLength = drawLength * 190;
    generations++;
    String newProduction = prod_;          
    newProduction = newProduction.replaceAll("F", rule_);
    return newProduction;
  }
}

class PentigreeLSystem extends LSystem {

  int steps = 1;
  float somestep = 0.1;
  float xoff = 1.01;

  PentigreeLSystem() {
    axiom = "F-F--F+F--F";
    rule = "F-F+F+F-F-F";
    startLength = 3.0;
    theta = radians(26);  
    reset();
  }

  void useRule(String r_) {
    rule = r_;
  }

  void useAxiom(String a_) {
    axiom = a_;
  }

  void useLength(float l_) {
    startLength = l_;
  }

  void useTheta(float t_) {
    theta = radians(t_);
  }

  void reset() {
    production = axiom;
    drawLength = startLength;
    generations = 0;
  }

  int getAge() {
    return generations;
  }

  void render() {
    translate(width/8, height/1);
    steps += 2;          
    if (steps > production.length()) {
      steps = production.length();
    }

    for (int i = 0; i < steps; i++) {
      char step = production.charAt(i);
      if (step == 'F') {
        noFill();
        stroke(125);
        line(0, 0, 0, -drawLength);
        translate(0, -drawLength);
      } 
      else if (step == '+') {
        rotate(theta);
      } 
      else if (step == '-') {
        rotate(-theta);
      } 
      else if (step == '[') {
        pushMatrix();
      } 
      else if (step == ']') {
        popMatrix();
      }
    }
  }

}


