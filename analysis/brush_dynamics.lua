-- Brush stroke dynamics estimator for a 40cm x 79cm linen canvas
-- All units SI unless stated otherwise.

local canvas = {
    width = 0.40,   -- meters
    height = 0.79   -- meters
}

local params = {
    texture_mm = 20.0,
    brush_mass = 0.12, -- kg
    gravity = 9.81,
    mu_base = 0.32,
    mu_texture_gain = 0.06,
    long_time = 0.45,  -- seconds
    short_time = 0.35, -- seconds
    rotation_angle = math.pi -- radians (180 deg sweep)
}

local function effective_friction(mu_base, gain, texture_mm)
    local normalized = math.min(texture_mm, 20.0) / 20.0
    return mu_base + gain * normalized
end

local function symmetric_accel(distance, duration)
    return 4.0 * distance / (duration * duration)
end

local function linear_metrics(length, duration, mass, mu, g)
    local speed = length / duration
    local accel = symmetric_accel(length, duration)
    local tension = mass * (accel + mu * g)
    return {
        length = length,
        duration = duration,
        speed = speed,
        acceleration = accel,
        tension = tension
    }
end

local function rotation_metrics(radius, theta, duration, mass, mu, g)
    local arc = radius * theta
    local speed = arc / duration
    local tangential_accel = symmetric_accel(arc, duration)
    local centripetal_accel = speed * speed / radius
    local tension = mass * (tangential_accel + centripetal_accel + mu * g)
    return {
        radius = radius,
        arc = arc,
        duration = duration,
        speed = speed,
        angular_speed = speed / radius,
        tangential_accel = tangential_accel,
        centripetal_accel = centripetal_accel,
        tension = tension
    }
end

local mu = effective_friction(params.mu_base, params.mu_texture_gain, params.texture_mm)

local linear_long = linear_metrics(canvas.height, params.long_time, params.brush_mass, mu, params.gravity)
local linear_short = linear_metrics(canvas.width, params.short_time, params.brush_mass, mu, params.gravity)

local half_diagonal = math.sqrt((canvas.width * 0.5)^2 + (canvas.height * 0.5)^2)
local rotation_long = rotation_metrics(half_diagonal, params.rotation_angle, params.long_time, params.brush_mass, mu, params.gravity)
local rotation_short = rotation_metrics(canvas.width * 0.5, params.rotation_angle, params.short_time, params.brush_mass, mu, params.gravity)

local function format_metrics(label, keys, data)
    print(string.format("%s:", label))
    for _, key in ipairs(keys) do
        local value = data[key]
        if value then
            print(string.format("  %-18s %.4f", key, value))
        end
    end
end

local linear_keys = { "length", "duration", "speed", "acceleration", "tension" }
local rotation_keys = {
    "radius",
    "arc",
    "duration",
    "speed",
    "angular_speed",
    "tangential_accel",
    "centripetal_accel",
    "tension"
}

print(string.format("Effective friction coefficient: %.4f", mu))
format_metrics("Linear long stroke", linear_keys, linear_long)
format_metrics("Linear short stroke", linear_keys, linear_short)
format_metrics("Rotational long sweep", rotation_keys, rotation_long)
format_metrics("Rotational short sweep", rotation_keys, rotation_short)
