import cv2
import sys
import os.path
import glob

#
# Literals
#

# execution parameters
MIN_SIZE    = 28
SAVE_EXT    = "png"
WINDOW_NAME = "Selection"

# Color definition
COLOR_RED   = (0,     0, 255)
COLOR_GREEN = (0,   255,   0)
COLOR_BLUE  = (255,   0,   0)
COLOR_WHITE = (255, 255, 255)
LINE_THICKNESS = 2

# Key code
KEY_ENTER   = 0xD
KEY_ESC     = 0x1B
KEY_L_ARROW = 0x250000
KEY_R_ARROW = 0x270000

#
# Represent the cascade classifier
#
class Classifier:

    # constructor
    def __init__(self, file):
        if not os.path.isfile(file):
            raise RuntimeError("%s: not found" % file)
        self.cascade = cv2.CascadeClassifier(file)

    # Detect faces from a BGR image
    def detect(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        areas = self.cascade.detectMultiScale(
            gray,
            # detector options
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(MIN_SIZE, MIN_SIZE))
        return areas

#
# Represent a candidate of classified area
#
class Candidate:
    # constructor, argument is a area
    def __init__(self, start, end):
        self.move_start(start)
        self.move_end(end)

    def move_start(self, start):
        self.sx, self.sy = start[0], start[1]

    def move_end(self, tail):
        self.ex, self.ey = tail[0], tail[1]

    # get start coordinate
    def locate_start(self):
        return (self.sx, self.sy)

    # get end coordinate
    def locate_end(self):
        return (self.ex, self.ey)

    # swap if the end coordinate is greater than the start
    def normalize(self):
        if(self.sx > self.ex):
            self.sx, self.ex = self.ex, self.sx
        if(self.sy > self.ey):
            self.sy, self.ey = self.ey, self.sy

    # get the width of this candidate
    def width(self):
        return (abs(self.ex - self.sx))

    # get the width of this candidate
    def height(self):
        return (abs(self.ey - self.sy))

    # check this candidate is valid one
    def invalid(self):
        tooSmall = (self.width() < MIN_SIZE) or (self.height() < MIN_SIZE)
        if(tooSmall):
            return True

        aspectRate = self.width() / self.height()
        if( (aspectRate > 1.1) or (aspectRate < 0.9) ):
            return True

        return False

    # check this candidate is all zero
    def invisible(self):
        visibility = self.width() + self.height()
        if(visibility > 0):
            return False
        return True

#
# Represent candidate selection window
#
class SelectionWindow:
    # constructor, argument is areas
    def __init__(self, image, candidates):
        self.candidates = candidates
        self.original = image
        self.canvas = None
        self.selection = Candidate( (0,0), (0,0) )
        self.index = 0

    # Callback of Mouse events
    def mouse_event(self, event, x, y, flags, param):

        # Left click event
        if (event == cv2.EVENT_LBUTTONDOWN):
            self.selection.move_start( (x, y) )
            self.selection.move_end((x, y))
        # Left drag event
        elif (flags == cv2.EVENT_FLAG_LBUTTON) and (event == cv2.EVENT_MOUSEMOVE):
            self.selection.move_end( (x, y) )
        else:
            pass

    # Choose a candidate,
    def choose_candidate(self, move):
        num = len(self.candidates)
        if (num == 0):
            return
        # move to left or right depend on move count
        self.index = (self.index + num + move) % num

        # copy the candidate to the selection
        candidate = self.candidates[self.index]
        self.selection.move_start( candidate.locate_start() )
        self.selection.move_end(candidate.locate_end())

    # Draw all of candidates
    def draw_candidates(self):
        for candidate in self.candidates:
            cv2.rectangle(self.canvas, candidate.locate_start(), candidate.locate_end(), COLOR_WHITE, LINE_THICKNESS)

    # Draw all of candidates
    def draw_selection(self):
        selection = self.selection
        if (selection.invisible()):
            return
        if (selection.invalid()):
            color = COLOR_RED
        else:
            color = COLOR_BLUE

        cv2.rectangle(self.canvas, selection.locate_start(), selection.locate_end(), color, LINE_THICKNESS)

    # Display the window and get selection
    def run(self):
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback(WINDOW_NAME, self.mouse_event)

        self.choose_candidate(0)

        while (1):
            self.canvas = self.original.copy()
            self.draw_candidates()
            self.draw_selection()

            cv2.imshow(WINDOW_NAME, self.canvas)
            key = cv2.waitKey(1)

            if (key == KEY_ENTER):
                # Correct the relation of start and end
                self.selection.normalize()
                break
            elif(key == KEY_ESC):
                # Invalidate the selection
                self.selection.move_start( (0,0) )
                self.selection.move_end( (0,0) )
                break;
            elif(key == KEY_L_ARROW):
                # Choose the left candidate
                self.choose_candidate(-1)
            elif (key == KEY_R_ARROW):
                # Choose the right candidate
                self.choose_candidate(1)
            else:
                pass

        return self.selection

# Detect candidates from the image
def detect(image, classifier):
    areas = classifier.detect(image)
    candidates = []
    for (x, y, w, h) in areas:
        candidates.append( Candidate( (x, y), (x+w, y+h) ) )
    return candidates

# Parse console option and create a list of image files from it
def parse_option():
    if len(sys.argv) != 3:
        sys.stderr.write("usage: %s <input directory> <output directory>\n" % os.path.basename(__file__))
        sys.exit(-1)

    input_dir = sys.argv[1]
    image_files = glob.glob(os.path.join(input_dir, "*.*"))
    if len(image_files) == 0:
        sys.stderr.write("Error! No image file found from " + input_dir)
        sys.exit(-1)

    output_dir = sys.argv[2]

    return image_files, output_dir

# Main funciton of this script
if __name__ == '__main__':

    # Get image filenames from console arguments
    image_files, save_dir = parse_option()

    # Setup Classifier (animeface)
    classifier = Classifier("lbpcascade_animeface.xml")

    # Create save directory
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    # Detect, extract and save for each image files
    save_count = 0
    for file in image_files:

        # Read the image file
        image = cv2.imread(file, cv2.IMREAD_COLOR)

        # Detect automatically
        candidates = detect(image, classifier)

        # Select partial image
        window = SelectionWindow(image, candidates)
        selection = window.run()

        # In this case, no valid area is selected
        if( (selection == None) or selection.invalid() ):
            print("Skipped", file)
            continue

        # Save to a image
        save_file = os.path.join(save_dir, ("%d.%s" % (save_count, SAVE_EXT) ))
        partimage = image[selection.sy:selection.ey, selection.sx:selection.ex]
        cv2.imwrite(save_file, partimage)

        print("File saved as ", save_file, ", corrdinate:", selection.locate_start(), selection.locate_end())
        save_count += 1
