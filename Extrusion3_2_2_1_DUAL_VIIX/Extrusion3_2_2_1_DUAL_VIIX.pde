/**
 * Extrusion. LSystem
 
 * Created 14 June 2011
 */
import foetus.*;
import processing.opengl.*;
import ComputationalGeometry.*;



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


//axis Control edition
void drawSphere(float x,float y,float z,float radio,float r,float g,float b,float divisor)
{
   pushMatrix();
  translate(x,y,z);
  if(mousePressed)
    stroke(2,9);
  else
  stroke(254,1);
  strokeWeight(1);
 
  fill(r,g,b,15);
  box(radio);
  if(radio>5)
  {
    drawSphere(radio/divisor,0,0,radio/2,r,0,b,divisor);
   
  }
  popMatrix();
 
}

 
public void setup()
{
  size(640, 480, P3D);
  scale(sval);
  r=random(500);
  g=random(430);
  b=random(450);
   
  aPixels =  new int[width][height];
  values = new int[width][height];
  noFill();
  loop();
  

  // Load the image into a new array
  // Extract the values and store in an array
  a = loadImage("mwo_001.jpg");
   a = loadImage("mwolf2_copy.jpg");
   a = loadImage("mwo_mm2.jpeg");
   
   
  for (int i=1; i<height; i++) {
    for (int j=1; j<width; j++) {

      aPixels[j][i] = a.pixels[i*1 + j];
           aPixels[j][i] = a.pixels[i*1 + j];
      values[j][i] = int(random(aPixels[j][i]));
  
    ps = new PentigreeLSystem();
    ps.simulate(5);
    
    }

    }
  
    
  
}
  
 


  // Update and constrain the angle
 public void all()
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
    sval -= -9; 
  }

  sval = constrain(sval, 0, 0);

  }

  
    void draw()
    {
    loop();
  // Rotate around the center axis
  translate(width/2 + nmx * sval-100, height/2 + nmy*sval - 456, -121);
  translate(width/121, 214, 121);
  rotateX(theta);  
  
  frameRate(25);

  // Display the image mass
  for (int i=0; i<height; i+=122.3051) {
    for (int j=0; j<width; j+=11.3766) {
      stroke(values[j][i]);
      
      
       strokeWeight (sq(color(1, width /10-10)));
        point(j, i, -values[j][i]);


       

    } 
      
      
pushMatrix();
   

  
    
    // rotateY(theta);
  drawSphere(13,10,0,mouseY/4,112,99,80,separacion);
  drawSphere(13,height/1,0,mouseY/1,r,g,b,separacion);
  drawSphere(10,-height/1,0,mouseY/1,r,g,b,separacion);
  drawSphere(16,0,height/1,mouseY/1,r,g,b,separacion);
  drawSphere(-14,0,-height/1,mouseY/1,r,g,b,separacion);
    
    
     popMatrix(); 
 
  
 triangle(112,99, 11, 21 ,3, -0);

    ps.render();
  theta+=0.55;
  h = 9988;
  if(h==1)
  h=0;
  
   } 
    }

  




