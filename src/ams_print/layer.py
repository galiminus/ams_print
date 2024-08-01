class Layer:
    def __init__(self, z, thickness, scale, size):
        self.z = z
        self.thickness = thickness
        self.scale = scale

        self.triangles = []
        self.vertices = {}

        self.grid = [[False for _ in range(size[1])] for _ in range(size[0])]

    def vertices_for(self, x, y):
        # Define the 8 vertices of the pixel
        scaled_x = x * self.scale
        scaled_y = y * self.scale

        vertices = [
            [scaled_x,               scaled_y,                self.z                  ],
            [scaled_x + self.scale,  scaled_y,                self.z                  ],
            [scaled_x + self.scale,  scaled_y + self.scale,   self.z                  ],
            [scaled_x,               scaled_y + self.scale,   self.z                  ],
            [scaled_x,               scaled_y,                self.z + self.thickness ],
            [scaled_x + self.scale,  scaled_y,                self.z + self.thickness ],
            [scaled_x + self.scale,  scaled_y + self.scale,   self.z + self.thickness ],
            [scaled_x,               scaled_y + self.scale,   self.z + self.thickness ]
        ]

        return vertices
    
    def put_pixel(self, x, y):
        self.grid[x][y] = True

    def put_floor(self, x, y):
        triangles = [
            [3, 1, 0],
            [3, 2, 1]
        ]

        for triangle in triangles:
            self.put_triangle(triangle=triangle, x=x, y=y)

    def put_ceiling(self, x, y):
        triangles = [
            [4, 5, 6],
            [4, 6, 7]
        ]

        for triangle in triangles:
            self.put_triangle(triangle=triangle, x=x, y=y)

    def put_left_wall(self, x, y):
        triangles = [
            [7, 3, 0],
            [4, 7, 0]
        ]

        for triangle in triangles:
            self.put_triangle(triangle=triangle, x=x, y=y)

    def put_right_wall(self, x, y):
        triangles = [
            [6, 5, 1],
            [6, 1, 2]
        ]

        for triangle in triangles:
            self.put_triangle(triangle=triangle, x=x, y=y)
    
    def put_top_wall(self, x, y):
        triangles = [
            [7, 6, 2],
            [3, 7, 2]
        ]

        for triangle in triangles:
            self.put_triangle(triangle=triangle, x=x, y=y)

    def put_bottom_wall(self, x, y):
        triangles = [
            [0, 5, 4],
            [1, 5, 0]
        ]

        for triangle in triangles:
            self.put_triangle(triangle=triangle, x=x, y=y)

    def put_triangle(self, x, y, triangle):
        vertices = self.vertices_for(x, y)

        global_vertex_indices = []

        for vertex_index in triangle:
            vertex = vertices[vertex_index]
            global_vertex_indices.append(self.find_or_create_vertex(vertex))

        self.triangles.append(global_vertex_indices)

    def find_or_create_vertex(self, vertex):
        rounded_vertex = tuple(map(lambda x: round(x, 4), vertex))
        vertex_key = 'x'.join(map(str, rounded_vertex))

        if vertex_key in self.vertices:
            return self.vertices[vertex_key]
        else:
            vertex_index = len(self.vertices)
            self.vertices[vertex_key] = vertex_index
            return vertex_index

    def build_geometry(self):
        self.triangles = []
        self.vertices = {}

        # For now we only have a top and bottom faces, we must add some walls
        for x in range(len(self.grid)):
            for y in range(len(self.grid[x])):
                if not self.grid[x][y]:
                    continue

                self.put_floor(x=x, y=y)
                self.put_ceiling(x=x, y=y)

                # Check if we need to add a wall on the left
                if x == 0 or not self.grid[x - 1][y]:
                    self.put_left_wall(x=x, y=y)

                # Check if we need to add a wall on the right
                if x == len(self.grid) - 1 or not self.grid[x + 1][y]:
                    self.put_right_wall(x=x, y=y)

                # Check if we need to add a wall on the bottom
                if y == 0 or not self.grid[x][y - 1]:
                    self.put_bottom_wall(x=x, y=y)

                # Check if we need to add a wall on the top
                if y == len(self.grid[x]) - 1 or not self.grid[x][y + 1]:
                    self.put_top_wall(x=x, y=y)
