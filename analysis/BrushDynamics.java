import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Brush stroke dynamics estimator aligned with the Lua reference implementation.
 */
public final class BrushDynamics {
    private static final double WIDTH = 0.40;      // m
    private static final double HEIGHT = 0.79;     // m
    private static final double TEXTURE_MM = 20.0; // mm cap
    private static final double BRUSH_MASS = 0.12; // kg
    private static final double GRAVITY = 9.81;    // m/s^2
    private static final double MU_BASE = 0.32;
    private static final double MU_TEXTURE_GAIN = 0.06;
    private static final double LONG_TIME = 0.45;  // s
    private static final double SHORT_TIME = 0.35; // s
    private static final double ROTATION_ANGLE = Math.PI; // rad (180 deg)

    private BrushDynamics() {}

    private static double effectiveFriction() {
        double normalized = Math.min(TEXTURE_MM, 20.0) / 20.0;
        return MU_BASE + MU_TEXTURE_GAIN * normalized;
    }

    private static double symmetricAccel(double distance, double duration) {
        return 4.0 * distance / (duration * duration);
    }

    private static Map<String, Double> linearMetrics(double length, double duration, double mass,
                                                     double mu, double g) {
        double speed = length / duration;
        double acceleration = symmetricAccel(length, duration);
        double tension = mass * (acceleration + mu * g);
        Map<String, Double> metrics = new LinkedHashMap<>();
        metrics.put("length", length);
        metrics.put("duration", duration);
        metrics.put("speed", speed);
        metrics.put("acceleration", acceleration);
        metrics.put("tension", tension);
        return metrics;
    }

    private static Map<String, Double> rotationMetrics(double radius, double theta, double duration,
                                                       double mass, double mu, double g) {
        double arc = radius * theta;
        double speed = arc / duration;
        double angularSpeed = speed / radius;
        double tangentialAccel = symmetricAccel(arc, duration);
        double centripetalAccel = speed * speed / radius;
        double tension = mass * (tangentialAccel + centripetalAccel + mu * g);
        Map<String, Double> metrics = new LinkedHashMap<>();
        metrics.put("radius", radius);
        metrics.put("arc", arc);
        metrics.put("duration", duration);
        metrics.put("speed", speed);
        metrics.put("angular_speed", angularSpeed);
        metrics.put("tangential_accel", tangentialAccel);
        metrics.put("centripetal_accel", centripetalAccel);
        metrics.put("tension", tension);
        return metrics;
    }

    private static void printMetrics(String label, Map<String, Double> metrics) {
        System.out.println(label + ":");
        metrics.forEach((key, value) -> System.out.printf("  %-18s %.4f%n", key, value));
    }

    public static void main(String[] args) {
        double mu = effectiveFriction();
        System.out.printf("Effective friction coefficient: %.4f%n", mu);

        Map<String, Double> linearLong = linearMetrics(HEIGHT, LONG_TIME, BRUSH_MASS, mu, GRAVITY);
        Map<String, Double> linearShort = linearMetrics(WIDTH, SHORT_TIME, BRUSH_MASS, mu, GRAVITY);

        double halfDiagonal = Math.hypot(WIDTH * 0.5, HEIGHT * 0.5);
        Map<String, Double> rotationLong = rotationMetrics(halfDiagonal, ROTATION_ANGLE, LONG_TIME,
                BRUSH_MASS, mu, GRAVITY);
        Map<String, Double> rotationShort = rotationMetrics(WIDTH * 0.5, ROTATION_ANGLE, SHORT_TIME,
                BRUSH_MASS, mu, GRAVITY);

        printMetrics("Linear long stroke", linearLong);
        printMetrics("Linear short stroke", linearShort);
        printMetrics("Rotational long sweep", rotationLong);
        printMetrics("Rotational short sweep", rotationShort);
    }
}
