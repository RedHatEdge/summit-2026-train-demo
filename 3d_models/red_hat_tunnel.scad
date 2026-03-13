// N-Scale Train Tunnel Bridge - "RED HAT"
// Solid tunnel, NO FLOOR (open bottom, sits over track)
// Letters cut through roof, brick texture on walls
$fn = 96;

outer_w    = 46.482;  arch_w = 35.56;  arch_h = 48.26;  outer_h = 53.34;
wall_len   = 148;
roof_thick = 5.0;
wall_thick = (outer_w - arch_w) / 2;  // side wall thickness ~5.5mm
font_size  = 24;  stroke_thicken = 0.8;
brick_h = 3.0;  brick_len = 6.0;  mortar_w = 0.6;  mortar_depth = 0.8;

module text_shape() {
    offset(delta = stroke_thicken)
        text("RED HAT", size = font_size,
             font = "Liberation Sans:style=Bold",
             halign = "center", valign = "center");
}
module arch_profile() {
    r = arch_w/2; rect_h = arch_h - r;
    union() { translate([-arch_w/2,0]) square([arch_w, rect_h]); translate([0,rect_h]) circle(r=r); }
}
module arch_solid() { rotate([90,0,90]) linear_extrude(height=500,center=true) arch_profile(); }

module side_wall_bricks(wall_y, y_dir) {
    zone_h = outer_h - roof_thick;
    rows = ceil(zone_h / (brick_h + mortar_w)) + 1;
    cols = ceil(wall_len / (brick_len + mortar_w)) + 1;
    dy = y_dir > 0 ? 0 : -mortar_depth - 0.01;
    for (r = [1:rows]) {
        z = r * (brick_h + mortar_w) - mortar_w/2;
        if (z < outer_h - roof_thick)
            translate([-wall_len/2, wall_y + dy, z])
                cube([wall_len, mortar_depth + 0.01, mortar_w]);
    }
    for (r = [0:rows]) {
        off = (r % 2 == 0) ? 0 : (brick_len + mortar_w) / 2;
        z_start = r * (brick_h + mortar_w);
        for (c = [0:cols]) {
            x = -wall_len/2 + off + c * (brick_len + mortar_w) - mortar_w/2;
            if (x > -wall_len/2 && x < wall_len/2 && z_start < outer_h - roof_thick)
                translate([x, wall_y + dy, z_start])
                    cube([mortar_w, mortar_depth + 0.01, min(brick_h + mortar_w, outer_h - roof_thick - z_start)]);
        }
    }
}

module end_wall_bricks(wall_x, x_dir) {
    zone_h = outer_h - roof_thick;
    rows = ceil(zone_h / (brick_h + mortar_w)) + 1;
    cols = ceil(outer_w / (brick_len + mortar_w)) + 1;
    dx = x_dir > 0 ? 0 : -mortar_depth - 0.01;
    for (r = [1:rows]) {
        z = r * (brick_h + mortar_w) - mortar_w/2;
        if (z < outer_h - roof_thick)
            translate([wall_x + dx, -outer_w/2, z])
                cube([mortar_depth + 0.01, outer_w, mortar_w]);
    }
    for (r = [0:rows]) {
        off = (r % 2 == 0) ? 0 : (brick_len + mortar_w) / 2;
        z_start = r * (brick_h + mortar_w);
        for (c = [0:cols]) {
            y = -outer_w/2 + off + c * (brick_len + mortar_w) - mortar_w/2;
            if (y > -outer_w/2 && y < outer_w/2 && z_start < outer_h - roof_thick)
                translate([wall_x + dx, y, z_start])
                    cube([mortar_depth + 0.01, mortar_w, min(brick_h + mortar_w, outer_h - roof_thick - z_start)]);
        }
    }
}

module inner_wall_bricks(wall_y, y_dir) {
    zone_h = arch_h;
    rows = ceil(zone_h / (brick_h + mortar_w)) + 1;
    cols = ceil(wall_len / (brick_len + mortar_w)) + 1;
    dy = y_dir > 0 ? 0 : -mortar_depth - 0.01;
    for (r = [1:rows]) {
        z = r * (brick_h + mortar_w) - mortar_w/2;
        if (z < arch_h)
            translate([-wall_len/2, wall_y + dy, z])
                cube([wall_len, mortar_depth + 0.01, mortar_w]);
    }
    for (r = [0:rows]) {
        off = (r % 2 == 0) ? 0 : (brick_len + mortar_w) / 2;
        z_start = r * (brick_h + mortar_w);
        for (c = [0:cols]) {
            x = -wall_len/2 + off + c * (brick_len + mortar_w) - mortar_w/2;
            if (x > -wall_len/2 && x < wall_len/2 && z_start < arch_h)
                translate([x, wall_y + dy, z_start])
                    cube([mortar_w, mortar_depth + 0.01, min(brick_h + mortar_w, arch_h - z_start)]);
        }
    }
}

// Tunnel shell: solid block minus arch, NO FLOOR
module tunnel_shell() {
    difference() {
        translate([-wall_len/2, -outer_w/2, 0])
            cube([wall_len, outer_w, outer_h]);
        // Arch goes all the way to Z=0 (open bottom)
        arch_solid();
    }
}

difference() {
    tunnel_shell();
    // Letters through roof
    translate([0, 0, outer_h - roof_thick - 0.1])
        linear_extrude(height = roof_thick + 0.2) text_shape();
    // Brick on all faces
    side_wall_bricks(-outer_w/2, 1);
    side_wall_bricks(outer_w/2, -1);
    end_wall_bricks(-wall_len/2, 1);
    end_wall_bricks(wall_len/2, -1);
    inner_wall_bricks(-arch_w/2, 1);
    inner_wall_bricks(arch_w/2, -1);
}
