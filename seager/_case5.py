from ._lemma2 import lemma2


def lVariables(self, d, p):
    self["l"] = self["k"] - (d // 2)    #Get level l in the tree (highest level path to target can reach)

    self["vl"] = p              #Get vl
    while self.tDict[self["vl"]].level != self["l"]:
        self["vl"] = self.tDict[self["vl"]].parent

    self["yl"] = p              #Get yl
    while self.tDict[self["yl"]].level != self["l"]:
        self["yl"] = self.tDict[self["yl"]].parent

    self["zl"] = p              #Get zl
    while self.tDict[self["zl"]].level != self["l"]:
        self["zl"] = self.tDict[self["zl"]].parent


def case5(self, p, w, d1, zkMinus):
    lVariables(self, d1, p)

    zkMinus2 = self.tDict[zkMinus].parent

    if zkMinus == self.tDict[zkMinus2].children[-1]:
        if self["vl"] == self["t"][-1]: return self.located(self["vl"])
        d2 = self.probe(self["vl"])
        return case5a(self, p, w, d1, d2)

    elif zkMinus == self.tDict[zkMinus2].children[0] and len(self.tDict[zkMinus2].children) > 1 and len(self.tDict[zkMinus].children) > 1:
        if self.tDict[zkMinus].parent == self["t"][-1]: return self.located(self.tDict[zkMinus].parent)
        d2 = self.probe(self.tDict[zkMinus].parent)
        return case5b(self, p, w, d1, d2)

    elif zkMinus != self.tDict[zkMinus2].children[-1] and len(self.tDict[zkMinus].children) < 2:
        return case5c(self, p, w, d1)
    
    raise Exception("Reached end of play function")


def case5a(self, p, w, d1, d2):
    wkPlus,  xkPlus  = self["dkPlus"][0],  self["dkPlus"][-1]
    ykMinus, zkMinus = self["dkMinus"][0], self["dkMinus"][-1]

    if d2 == (d1 // 2) + 2:
        return self.lemma4(wkPlus, xkPlus, self.tDict[wkPlus].level + 1)

    elif d2 == (d1 // 2) + 1:
        return self.lemma4(self.tDict[wkPlus].parent, self.tDict[xkPlus].parent, self.tDict[wkPlus].level)

    elif d2 == (d1 // 2) - 1:
        return self.lemma4(self.tDict[ykMinus].parent, self.tDict[zkMinus].parent, self.tDict[ykMinus].level)

    elif d2 == (d1 // 2) - 2:
        ykMinus2, zkMinus2 = self.tDict[ykMinus].parent,  self.tDict[zkMinus].parent

        if d1 != 6:
            ykMinus3, zkMinus3 = self.tDict[ykMinus2].parent, self.tDict[zkMinus2].parent

            return self.lemma4(ykMinus3, zkMinus3, self.tDict[zkMinus2].level)

        elif d1 == 6:
            return lemma2(self, self.tDict[ykMinus2].parent, ykMinus2, zkMinus2)

    elif d2 == d1 // 2:
        return self.lemma4(self.tDict[self.tDict[wkPlus].parent].parent, zkMinus, self.tDict[zkMinus].level + 1)

    elif d2 == d1:
        print("dkMinus:", self["dkMinus"])
        print("dk:", self["dk"])
        print("dkPlus:", self["dkPlus"])

    raise Exception("End of Func. d2: " + str(d2) + "d1: " + str(d1))
    

def case5b(self, p, w, d1, d2):
    wk = self.tDict[self["dkPlus"][0]].parent
    xk = self.tDict[self["dkPlus"][-1]].parent

    zkMinus  = self["dkMinus"][-1]
    zkMinus2 = self.tDict[zkMinus].parent

    zlPlus = self["dkMinus"][-1]

    while self.tDict[zlPlus].level != self["l"]+ 1:
        zlPlus = self.tDict[zlPlus].parent

    if d2 == 1:
        return self.located(zkMinus)

    elif d2 == 2:
        return self.lemma4(self["dkMinus"][-1], self["dkMinus"][-1], self.tDict[self["dkMinus"][-1]].level + 1)
        
    elif d2 == d1:
        return self.lemma4(self.tDict[self.tDict[self["dkPlus"][0]].parent].parent, self.tDict[self.tDict[self["dkPlus"][-1]].parent].parent, self.tDict[self["dkPlus"][0]].level + 1)

    elif d2 == d1 - 1:
        return self.lemma4(wk, xk, self.tDict[wk].level + 1)

    elif d2 == d1 - 2:
        kMinus   = self.lDict[self["k"] - 1]

        for i in range(len(kMinus) - 1, 0, -1):
            r = kMinus[i]

            while r != zlPlus and r != self["zl"]:
                r = self.tDict[r].parent

            if r == self["zl"]:
                t = kMinus[i]
                break

        return self.lemma4(self.tDict[wk].parent, t, self.tDict[wk].level + 1)

    return case5bExtraCase(self, zkMinus2, w, d1, d2)


def case5bExtraCase(self, p, w, d1, d2):
    #d2 is odd with 3 <= d2 <= d1 - 3 or similarly for case 5c
    if d2 % 2 != 0 and (3 <= d2 <= d1 - 3 or 5 <= d2 <= d1 + 2):
        m = (d2 - 1) / 2
        levelPlus = self["k"] - m - 1

        stPlus = self["dkMinus"][-1]
        while self.tDict[stPlus].level != levelPlus:
            stPlus = self.tDict[stPlus].parent

        stRoot = self.tDict[stPlus].parent

        kMinus   = self.lDict[self["k"] - 1]

        for i in range(len(kMinus) - 1, 0, -1):
            r = kMinus[i]

            while r != stPlus and r != stRoot:
                r = self.tDict[r].parent

            if r == stRoot:
                t = kMinus[i]
                break

        for i in range(0, len(kMinus)):
            r = kMinus[i]

            while r != stPlus and r != stRoot:
                r = self.tDict[r].parent

            if r == stRoot:
                s = kMinus[i]
                break

        return self.lemma4(s, t, self.tDict[s].level + 1)

    elif d2 % 2 == 0 and (4 <= d2 <= d1 - 4 or 6 <= d2 <= d1 + 2):
        m = d2 / 2

        q, R, s, t = None, None, None, None

        qrPlus = self["dkMinus"][-1]
        while qrPlus is not None and self.tDict[qrPlus].level != self["k"] - m:
            qrPlus = self.tDict[qrPlus].parent

        if qrPlus is not None:
            qrRoot = self.tDict[qrPlus].parent

            levelK   = self.lDict[self["k"]]

            for i in range(len(levelK) - 1, 0, -1):
                r = levelK[i]

                while r != qrPlus and r != qrRoot and r != None:
                    r = self.tDict[r].parent

                if r == qrRoot:
                    R = levelK[i]
                    break

            for i in range(0, len(levelK)):
                r = levelK[i]

                while r != qrPlus and r != qrRoot and r != None:
                    r = self.tDict[r].parent

                if r == qrRoot:
                    q = levelK[i]
                    break


        stPlus = self["dkMinus"][-1]
        while stPlus is not None and self.tDict[stPlus].level != self["k"] - m - 1:
            stPlus = self.tDict[stPlus].parent

        if stPlus is not None:
            stRoot = self.tDict[stPlus].parent

            kMinusMinus   = self.lDict[self["k"] - 2]

            for i in range(len(kMinusMinus) - 1, 0, -1):
                r = kMinusMinus[i]

                while r != stPlus and r != stRoot and r != None:
                    r = self.tDict[r].parent

                if r == stRoot:
                    t = kMinusMinus[i]
                    break

            for i in range(0, len(kMinusMinus)):
                r = kMinusMinus[i]

                while r != stPlus and r != stRoot and r != None:
                    r = self.tDict[r].parent

                if r == stRoot:
                    s = kMinusMinus[i]
                    break

        if q == None and R == None and s == None and t == None:
            raise Exception("====== ALL OF S, T, Q, R, ARE NONE ======")

        elif q == None or R == None or self.children(q, R) == []:
            return self.lemma4(s, t, self.tDict[s].level + 1)

        elif s == None or t == None or self.children(s, t) == []:
            return self.lemma4(q, R, self.tDict[q].level + 1)

        lVariables(self, d2, p)
        if self["vl"] == self["t"][-1]: return self.located(self["vl"])
        d3 = self.probe(self["vl"])

        self["dkMinus"] = self.children(self.tDict[s].parent, self.tDict[t].parent)
        self["dk"]      = []
        self["dkPlus"]  = self.children(self.tDict[q].parent, self.tDict[R].parent)

        self["k"] = self.tDict[s].level + 1

        return case5a(self, p, w, d1, d3)


def case5c(self, p, w, d1):    
    zkMinus  = self["dkMinus"][-1]
    zkMinus2 = self.tDict[zkMinus].parent
    zk       = self.tDict[zkMinus].children[0]
    zkMinusPred   = self["dkMinus"][self["dkMinus"].index(zkMinus) - 1]

    if zk == self["t"][-1]: return self.located(zk)
    d2 = self.probe(zk)

    if d2 == 1:
        return self.located(self["dkMinus"][-1])

    elif d2 == 2:
        return self.located(self.tDict[self["dkMinus"][-1]].parent)

    elif d2 == 3:
        t = self.tDict[zkMinus2].children[0]

        return lemma2(self, zkMinus2, t, zkMinusPred)

    elif d2 == 4:
        zkMinus3 = self.tDict[zkMinus2].parent
        if zkMinus3 == self["t"][-1]: return self.located(zkMinus3)
        d3 = self.probe(zkMinus3)

        if d3 == 1:
            zkMinus3Children = self.tDict[zkMinus3].children
            s = zkMinus3Children[0]
            zkMinus2Pred = zkMinus3Children[zkMinus3Children.index(zkMinus2) - 1]

            return lemma2(self, zkMinus3, s, zkMinus2Pred)

        elif d3 == 2:
            return case5(self, p, w, d1, zkMinusPred)

        elif d3 == 3:
            return self.lemma4(t, zkMinusPred, self.tDict[t].level + 1)

        elif d3 == 4:
            q = self.tDict[t].children[0]
            r = self.tDict[zkMinusPred][-1]

            return self.lemma4(q, r, self.tDict[r].level + 1)

    elif 5 <= d2 <= d1 + 2:
        return case5b(self, p, w, d1, d2)
    
    raise Exception("Reached end of play function")
