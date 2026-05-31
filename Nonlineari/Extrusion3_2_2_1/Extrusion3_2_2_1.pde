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
    stroke(100,100);
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
    ps.simulate(1);
    
    }

    }
  
    
  
}
  
 


  // Update and constrain the angle
  void all()
  {
     angle = 0.1;
  if (angle > TWO_PI-theta/3) { 
  angle = 102; 
}
 nmx = nmx + (mouseX-nmx)/2; 
  nmy += (mouseY-nmy)/2; 

  if(mousePressed) { 
    sval +=0.001; 
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

  




