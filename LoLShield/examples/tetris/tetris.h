/**
 * The coord struct holds an (x,y) pair, as used in the pieces declarations
 * an in the position structure.
 */
typedef struct coord {
  int8_t x;
  int8_t y;
} coord_t;

/**
 * One piece view. Each Tetris piece may have one to four views.
 */
typedef struct pieceView {
  coord_t elements[4];
} pieceView_t;

/**
 * One Tetris piece object, made of one to four views.
 */
typedef struct piece {
  pieceView_t** views;
  uint8_t numViews;
} piece_t;

/**
 * Structure to hold the current position and view of the piece
 * being played.
 */
typedef struct pos {
  coord_t coord;
  uint8_t view;
} pos_t;
