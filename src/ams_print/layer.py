class Layer:
    def __init__(self, size):
        self.triangles = []
        self.vertices = {}

        self.grid = [[False for _ in range(size[1])] for _ in range(size[0])]

    def vertices_for(self, x, y, z, thickness, scale):
        # Define the 8 vertices of the pixel
        scaled_x = x * scale
        scaled_y = y * scale

        vertices = [
            [  scaled_x,          scaled_y,           z              ],
            [  scaled_x + scale,  scaled_y,           z              ],
            [  scaled_x + scale,  scaled_y + scale,   z              ],
            [  scaled_x,          scaled_y + scale,   z              ],
            [  scaled_x,          scaled_y,           z + thickness  ],
            [  scaled_x + scale,  scaled_y,           z + thickness  ],
            [  scaled_x + scale,  scaled_y + scale,   z + thickness  ],
            [  scaled_x,          scaled_y + scale,   z + thickness  ]
        ]

        return vertices
    
    def plot(self, x, y):
        self.grid[x][y] = True

    def put_floor(self, x, y, z, thickness, scale):
        triangles = [
            [3, 1, 0],
            [3, 2, 1]
        ]

        for triangle in triangles:
            self.put_triangle(triangle, x, y, z, thickness, scale)

    def put_ceiling(self, x, y, z, thickness, scale):
        triangles = [
            [4, 5, 6],
            [4, 6, 7]
        ]

        for triangle in triangles:
            self.put_triangle(triangle, x, y, z, thickness, scale)

    def put_left_wall(self, x, y, z, thickness, scale):
        triangles = [
            [7, 3, 0],
            [4, 7, 0]
        ]

        for triangle in triangles:
            self.put_triangle(triangle, x, y, z, thickness, scale)

    def put_right_wall(self, x, y, z, thickness, scale):
        triangles = [
            [6, 5, 1],
            [6, 1, 2]
        ]

        for triangle in triangles:
            self.put_triangle(triangle, x, y, z, thickness, scale)
    
    def put_top_wall(self, x, y, z, thickness, scale):
        triangles = [
            [7, 6, 2],
            [3, 7, 2]
        ]

        for triangle in triangles:
            self.put_triangle(triangle, x, y, z, thickness, scale)

    def put_bottom_wall(self, x, y, z, thickness, scale):
        triangles = [
            [0, 5, 4],
            [1, 5, 0]
        ]

        for triangle in triangles:
            self.put_triangle(triangle, x, y, z, thickness, scale)

    def put_triangle(self, triangle, x, y, z, thickness, scale):
        vertices = self.vertices_for(x, y, z, thickness, scale)

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

    def build_geometry(self, z, thickness, scale):
        self.triangles = []
        self.vertices = {}

        # For now we only have a top and bottom faces, we must add some walls
        for x in range(len(self.grid)):
            for y in range(len(self.grid[x])):
                if not self.grid[x][y]:
                    continue

                self.put_floor(x, y, z, thickness, scale)
                self.put_ceiling(x, y, z, thickness, scale)

                # Check if we need to add a wall on the left
                if x == 0 or not self.grid[x - 1][y]:
                    self.put_left_wall(x, y, z, thickness, scale)

                # Check if we need to add a wall on the right
                if x == len(self.grid) - 1 or not self.grid[x + 1][y]:
                    self.put_right_wall(x, y, z, thickness, scale)

                # Check if we need to add a wall on the bottom
                if y == 0 or not self.grid[x][y - 1]:
                    self.put_bottom_wall(x, y, z, thickness, scale)

                # Check if we need to add a wall on the top
                if y == len(self.grid[x]) - 1 or not self.grid[x][y + 1]:
                    self.put_top_wall(x, y, z, thickness, scale)
