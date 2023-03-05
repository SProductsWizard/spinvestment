import os
import sys
import numpy as np
import re

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


class SPCFUtils:
    @staticmethod
    def convertStrFloat(numStr):
        multiple = 1
        numStr = numStr.replace("$", "")
        numStr = numStr.replace(",", "")
        if "%" in numStr:
            multiple = 0.01
            numStr = numStr.replace("%", "")
        if "mm" in numStr:
            multiple = 1e6
            numStr = numStr.replace("mm", "")

        return float(numStr) * multiple

    @staticmethod
    def convertIntexRamp(intexSyntax, term, divisor=1, forceInt=False):
        intexSyntax = intexSyntax.lower()

        if "ramp" in intexSyntax:
            for rampMatch in re.findall(
                r"(\d+\.*\d* +ramp +\d+ +\d+\.*\d*)", intexSyntax
            ):

                rampMatchSplit = rampMatch.split(" ")
                rangeStart = float(rampMatchSplit[0])
                rangeEnd = float(rampMatchSplit[-1])
                rangeTimes = int(rampMatchSplit[-2])

                rampRange = np.linspace(rangeStart, rangeEnd, num=rangeTimes)

                rampList = [f"{item:.2f}" for item in list(rampRange)]

                rampStr = " ".join(rampList)

                intexSyntax = intexSyntax.replace(rampMatch, rampStr)

        if "for" in intexSyntax:
            for forMatch in re.findall(r"(\d+\.*\d* +for +\d+)", intexSyntax):
                forMatchSplit = forMatch.split(" ")
                forList = [forMatchSplit[0]] * int(forMatchSplit[-1])
                forStr = " ".join(forList)
                intexSyntax = intexSyntax.replace(forMatch, forStr)

        intexSyntaxSplit = re.split(r" +", intexSyntax)

        # pad or truncate
        intexSyntaxSplitExtend = intexSyntaxSplit[:term] + [intexSyntaxSplit[-1]] * (
            term - len(intexSyntaxSplit)
        )

        if forceInt:
            res = [int(float(item) / divisor) for item in intexSyntaxSplitExtend]
        else:
            res = [float(item) / divisor for item in intexSyntaxSplitExtend]

        return res

    @staticmethod
    def financeFormatNumber(rawNum, formatType):

        if formatType == "pct0":
            res = "{:.0%}".format(rawNum)
        elif formatType == "pct2":
            res = "{:.2%}".format(rawNum)
        elif formatType == "comma":
            res = f"{rawNum:,.0f}"
        elif formatType == "comma2":
            res = f"{rawNum:,.2f}"
        return res
