import cv2 as cv
import numpy as np

# vid = cv.VideoCapture("test.mkv")
# vid = cv.VideoCapture("test2.mp4")
vid = cv.VideoCapture("synctest2.mkv")
i = 0


def printf(x):
    print(x, flush=True)


def findSyncStart(vid_fname):
    cap = cv.VideoCapture(vid_fname)
    foundblack = foundpurple = False
    i = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            cap.release()
            return None

        gray = cv.cvtColor(frame[:10, :10], cv.COLOR_BGR2GRAY)
        isblack = gray[5, 5] < 1

        if not foundblack:
            if isblack:
                # printf("foundblack {}".format(i))
                foundblack = True
        elif not foundpurple:
            if not isblack:
                # printf("foundpurple {}".format(i))
                foundpurple = True
        elif isblack:
            cap.release()
            return (i - 180)  # sync frame - 3s at 60fps

        i += 1;
        continue
    cap.release()
    return None


printf(findSyncStart("synctest2.mkv"))

# while vid.isOpened():
#     ret, frame = vid.read()

#     if not ret:
#         printf("Can't receive frame: {}".format(i))
#         break

#     if gamestart is None:
#         gray =cv.cvtColor(frame[:10,:10], cv.COLOR_BGR2GRAY)
#         isblack = gray[5,5] > 1

#         if not foundblack:
#             if isblack:
#                 printf("Found black on {}".format(i))
#                 foundblack = True
#         elif not foundpurple:
#             if not isblack:
#                 printf("Found purple on {}".format(i))
#                 foundpurple = True
#         elif isblack:
#             printf("Purple end on {}".format(i))
#             gamestart = i - 180 #sync frame - 3s at 60fps
#         i += 1; continue

#     if not foundblack:
#         if gray[5,5] > 1:
#             i += 1
#             continue
#         else:
#             printf("Foundblack on {}".format(i))
#             foundblack = True

#     if foundblack and (not foundpurple):
#         if gray[5,5] <= 1:
#             i += 1
#             continue
#         else:
#             printf("Foundpurple on {}".format(i))
#             foundpurple = True

#     if foundpurple and purpleend == 0:
#         if gray[5,5] > 1:
#             i+=1
#             continue
#         else:
#             printf("Purpleend on {}".format(i))
#             purpleend = i

#     if purpleend > 0 and not newpurple:
#         if gray[5,5] <= 1:
#             i += 1
#             continue
#         else:
#             newpurple = True
#             printf("Newpurple on {}".format(i))
#     # p00 = frame[0,0]
#     # p10 = frame[1,0]

#     # printf(p00)
#     # printf(p10)
#     im = cv.resize(frame[:25, :25], (512,512), 0, 0, interpolation = cv.INTER_NEAREST)
#     # if i%5 == 0:
#     printf(i)
#     cv.imshow("close", im)
#     if cv.waitKey(0) == ord('q'):
#         break
#     i += 1

# vid.release()
# cv.destroyAllWindows()
