"""
this class is responsible for the storing the current states of a chess game
"""


class GameState():
    def __init__(self):
        # first character is color of piece(b or w)
        # second character is type of piece(R,K,Q,p,B)
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveFunctions = {"R": self.getRookMoves,"p":self.getPawnMoves,"N":self.getKnightMoves,"B":self.getBishopMoves,"Q":self.getQueenMoves
                              ,"K": self.getKingMoves
                              }
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible =()
        self.currentCastlingRights = CastleRights(True,True,True,True)
        self.castleRightsLog =[CastleRights(self.currentCastlingRights.wks,self.currentCastlingRights.bks,self.currentCastlingRights.wqs,self.currentCastlingRights.bqs)]

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        if move.pieceMoved =="wK":
            self.whiteKingLocation = (move.endRow,move.endCol)
        elif move.pieceMoved =="bK":
            self.blackKingLocation = (move.endRow,move.endCol)
        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0]+'Q'
        # enPassant
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol]="--"
        if move.pieceMoved[1]=='p' and abs(move.startRow-move.endRow) == 2:
            self.enpassantPossible =((move.startRow + move.endRow)//2 ,move.startCol)
        else:
            self.enpassantPossible =()


        # castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol-1] =self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1] ="--"
            else:
                self.board[move.endRow][move.endCol+1]=self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] ="--"

        # update castling rights
        self.updateCastlingRights(move)
        self.castleRightsLog .append(CastleRights(self.currentCastlingRights.wks,self.currentCastlingRights.bks,self.currentCastlingRights.wqs,self.currentCastlingRights.bqs))


    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCapture
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved =="wK":
                self.whiteKingLocation = (move.startRow,move.startCol)
            elif move.pieceMoved =="bK":
                self.blackKingLocation = (move.startRow,move.startCol)
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] =move.pieceCapture
                self.enpassantPossible =(move.endRow,move.endCol)
            if move.pieceMoved[1]== 'p' and abs(move.startRow - move.endRow):
                self.enpassantPossible =()
            self.castleRightsLog.pop()
            self.currentCastlingRights  = self.castleRightsLog[-1]
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol -1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else:
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol +1]
                    self.board[move.endRow][move.endCol+1] = '--'
            self.checkMate = False
            self.staleMate = False
    
    def updateCastlingRights(self,move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved =='wR':
            if move.startRow == 7:
                if move.startCol ==0:
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved =='bR':
            if move.startRow == 0:
                if move.startCol ==0:
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.bks = False



    def getvalidMoves(self):
        tempEnpassantPossible =self.enpassantPossible
        tempCastleRights =CastleRights(self.currentCastlingRights.wks,self.currentCastlingRights.bks,self.currentCastlingRights.wqs,self.currentCastlingRights.bqs)
        moves = self.getAllPossibleMoves()
        legalMoves =[]
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0],self.whiteKingLocation[1],moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0],self.blackKingLocation[1],moves)


        for i in range(len(moves)-1,-1,-1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove #black
            if not self.inCheck():
                # print(moves[i].getchessNotation())
                legalMoves.append(moves[i])
            self.whiteToMove = not self.whiteToMove #white
            self.undoMove()
        print(len(legalMoves))
        if len(legalMoves) == 0:
            if self.inCheck():
                self.checkMate =True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False 
        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRights =tempCastleRights
        return legalMoves
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0],self.whiteKingLocation[1])
        else: 
            return self.squareUnderAttack(self.blackKingLocation[0],self.blackKingLocation[1])
    def squareUnderAttack(self,r,c):
        self.whiteToMove = not self.whiteToMove#b
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove#w
        for move in oppMoves:
            if move.endRow == r and move.endCol == c: 
                return True
        return False

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r,c,moves)
        return moves
    
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:
            if self.board[r - 1][c] == "--":  # 1 square pawn advance
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":  # 2 square pawn advance
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r - 1][c - 1][0] == "b":  # Capture to the left
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True))
            if c + 1 <= 7:
                if self.board[r - 1][c + 1][0] == "b":  # Capture to the right
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True))
        else:
            if self.board[r + 1][c] == "--":  # 1 square pawn advance
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":  # 2 square pawn advance
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == "w":  # Capture to the left
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True))
            if c + 1 <= 7:
                if self.board[r + 1][c + 1][0] == "w":  # Capture to the right
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True))

    def getRookMoves(self,r,c,moves):
        direction = ((-1,0),(0,-1),(0,1),(1,0))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in direction:
            for i in range(1,8):
                endRow = r + d[0]*i
                endCol = c + d[1]*i
                if 0<= endCol< 8 and  0 <= endRow <8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece =="--":
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    else:# own pieces
                        break
                else:
                    break
    
    def getBishopMoves(self,r,c,moves):
        # print("heare")
        direction = ((-1,1),(1,-1),(1,1),(-1,-1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in direction:
            for i in range(1,8):
                endRow = r + d[0]*i
                endCol = c + d[1]*i
                if 0 <= endCol< 8 and  0 <= endRow <8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    else:# own pieces
                        break
                else:
                    break
    def getKnightMoves(self,r,c,moves):
       
        direction = ((-1,2),(2,-1),(2,1),(1,2),(-2,-1),(-1,-2),(1,-2),(-2,1))
        enemyColor = "w" if self.whiteToMove else "b"
        for d in direction:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0<= endCol< 8 and  0 <= endRow <8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != enemyColor:
                    moves.append(Move((r,c),(endRow,endCol),self.board))
                        
    def getQueenMoves(self,r,c,moves):
        self.getRookMoves(r,c,moves)
        self.getBishopMoves(r,c,moves)

    def getKingMoves(self,r,c,moves):
        direction = ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))
        enemyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + direction[i][0]
            endCol = c + direction[i][1]
            if 0 <= endCol< 8 and  0 <= endRow <8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != enemyColor:
                    moves.append(Move((r,c),(endRow,endCol),self.board))   

    def getCastleMoves(self,r,c,moves):
        if self.inCheck():
            return 
        if (self.whiteToMove and self.currentCastlingRights.wks) or(not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(r,c,moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or(not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(r, c,moves)
    def getKingsideCastleMoves(self,r,c,moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] =="--":
            if not self.squareUnderAttack(r,c+1) and not self.squareUnderAttack(r,c+2):
                moves.append(Move((r,c),(r,c+2),self.board,isCastleMove=True))


    def getQueensideCastleMoves(self,r,c,moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] =="--" and self.board[r][c-3]:
            if not self.squareUnderAttack(r,c-1) and not self.squareUnderAttack(r,c-2) and not self.squareUnderAttack(r,c-3):
                moves.append(Move((r,c),(r,c-2),self.board,isCastleMove=True))

class CastleRights():
    def __init__(self,wks,bks,wqs,bqs):
        self.wks = wks
        self.bks = bks
        self.bqs =bqs
        self.wqs = wqs
        

class Move():
    rankstoRows = {"1": 7,
                   "2": 6,
                   "3": 5,
                   "4": 4,
                   "5": 3,
                   "6": 2,
                   "7": 1,
                   "8": 0
                   }

    rowsToRanks = {v: k for k, v in rankstoRows.items()}
    filesToCols = {"a": 0,
                   "b": 1,
                   "c": 2,
                   "d": 3,
                   "e": 4,
                   "f": 5,
                   "g": 6,
                   "h": 7
                   }
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board,isEnpassantMove=False,isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCapture = board[self.endRow][self.endCol]
        self.isPawnPromotion = False

        if (self.pieceMoved =='wp' and self.endRow == 0) or (self.pieceMoved =='bp' and self.endRow == 7):
            self.isPawnPromotion = True
        self.moveID = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol
        #en passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCapture ='wp'  if self.pieceMoved == 'bp' else 'bp'
        self.isCastleMove = isCastleMove

        
        # print(self.moveID)
    def __eq__(self,other):
        if isinstance(other,Move):
            return self.moveID == other.moveID
        return False
    def getchessNotation(self):
        return self.getRankFile(self.startRow, self.startCol)+self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c]+self.rowsToRanks[r]
