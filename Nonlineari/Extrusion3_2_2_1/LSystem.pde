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
    theta = radians(21.0);
    reset();
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

