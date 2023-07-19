class intCmdInput:
    def default(hasAMin, hasAMax, strict, min, max, restriction):
        hasAMin = bool(hasAMin)
        hasAMax = bool(hasAMax)
        strict = bool(strict)
        min = int(min)
        max = int(max)
        restriction = str(restriction)

    
        allIsFine = bool(None)
        answer = int(0)
        CmdInput = str(None)
        errorMessage = str(None)
        specifiedRestriction = "" if len(restriction) == 0 else "Restriction! Your int must " + restriction
        print("Please enter an integer. " + specifiedRestriction)

        while not(allIsFine):
            errorMessage = ""
            CmdInput = str(input())
            try:
                answer = int(CmdInput)
                if hasAMin | hasAMax:
                    tooSmall = answer <= min if strict == True else answer < min
                    tooBig = answer >= max if strict == True else answer > max
                    if hasAMin & hasAMax:
                        if tooSmall | tooBig:
                            errorMessage = specifiedRestriction
                    elif hasAMin:
                        if tooSmall:
                            errorMessage = specifiedRestriction
                    elif tooBig:
                        errorMessage = specifiedRestriction
            except:
                errorMessage = "Your int is not valid."
            
            allIsFine = len(errorMessage) == 0

            if not(allIsFine):
                errorMessage += " Please retry: "
                print(errorMessage)

        return answer



class ValidInputs:
    def IntCMDInput():
        return intCmdInput.default(False, False, False, 0, 0, "")

    def IntCMDInputGreaterThan(minimumValue):
        return intCmdInput.default(True, False, True, minimumValue, 0, f"be strictly superior than {minimumValue}.")

    def IntCMDInputAtLeast(minValue):
        return intCmdInput.default(True, False, False, minValue, 0, f"be at least {minValue}.")

    def IntCMDInputSmallerThan(maximumValue):
        return intCmdInput.default(False, True, True, 0, maximumValue, f"be strictly inferior than {maximumValue}.")

    def IntCMDInputAtMost(maxValue):
        return intCmdInput.default(False, True, False, 0, maxValue, f"be at most {maxValue}.")

    def IntCMDInputBetween(minimumBorn, maximumBorn):
        return intCmdInput.default(True, True, True, minimumBorn, maximumBorn, f"be between {minimumBorn} and {maximumBorn}.")

    def IntCMDInputFromA(minBorn, maxBorn):
        return intCmdInput.default(True, True, False, minBorn, maxBorn, f"go from {minBorn} to {maxBorn} inclusively.")

    def IntCMDInputPositiveOrNul():
        return ValidInputs.IntCMDInputAtLeast(0)

    def IntCMDInputStrictlyPositive():
        return ValidInputs.IntCMDInputGreaterThan(0)

    def IntCMDInputNegativeOrNul():
        return ValidInputs.IntCMDInputAtMost(0)

    def IntCMDInputStrictlyNegative():
        return ValidInputs.IntCMDInputSmallerThan(0)


    #Float version
    def FloatCMDInput():
        return floatCmdInput.default(False, False, False, 0.0, 0.0, "")

    def FloatCMDInputGreaterThan(minimumValue):
        return floatCmdInput.default(True, False, True, minimumValue, 0.0, f"be strictly superior than {minimumValue}.")

    def FloatCMDInputAtLeast(minValue):
        return floatCmdInput.default(True, False, False, minValue, 0.0, f"be at least {minValue}.")

    def FloatCMDInputSmallerThan(maximumValue):
        return floatCmdInput.default(False, True, True, 0.0, maximumValue, f"be strictly inferior than {maximumValue}.")

    def FloatCMDInputAtMost(maxValue):
        return floatCmdInput.default(False, True, False, 0.0, maxValue, f"be at most {maxValue}.")

    def FloatCMDInputBetween(minimumBorn, maximumBorn):
        return floatCmdInput.default(True, True, True, minimumBorn, maximumBorn, f"be between {minimumBorn} and {maximumBorn}.")

    def FloatCMDInputFromA(minBorn, maxBorn):
        return floatCmdInput.default(True, True, False, minBorn, maxBorn, f"go from {minBorn} to {maxBorn} inclusively.")

    def FloatCMDInputPositiveOrNul():
        return ValidInputs.FloatCMDInputAtLeast(0)

    def FloatCMDInputStrictlyPositive():
        return ValidInputs.FloatCMDInputGreaterThan(0)

    def FloatCMDInputNegativeOrNul():
        return ValidInputs.FloatCMDInputAtMost(0)

    def FloatCMDInputStrictlyNegative():
        return ValidInputs.FloatCMDInputSmallerThan(0)

class StrCmdInput:
    def default(question):
        question = str(question)
        allIsFine = bool(None)
        answerIsYes = True
        errorMessage = str(None)
        CmdInput = str(None)
        firstCharacter = str(None)

        print(question + "(Y/n)? ")
        while not(allIsFine):
            errorMessage = ""
            CmdInput = str(input())
            if len(CmdInput) == 1:
                firstCharacter = CmdInput.lower()[0]
                answerIsYes = True if firstCharacter == 'y' else False
                if (not(answerIsYes) and (firstCharacter != 'n')):
                    errorMessage = "Your answer must be 'y' or 'n'. (Uppercase allowed)"
            else:
                errorMessage = "A valid input in this case only implies one caracter, either the first of 'yes' or 'no'."
            
            allIsFine = len(errorMessage) == 0

            if not(allIsFine):
                errorMessage = "Please restart: "
                print(errorMessage)

        return answerIsYes


class floatCmdInput:
    def default(hasAMin, hasAMax, strict, min, max, restriction):
        hasAMin = bool(hasAMin)
        hasAMax = bool(hasAMax)
        strict = bool(strict)
        min = float(min)
        max = float(max)
        restriction = str(restriction)

    
        allIsFine = bool(None)
        answer = float(0.0)
        CmdInput = str(None)
        errorMessage = str(None)
        specifiedRestriction = "" if len(restriction) == 0 else "Restriction! Your float must " + restriction
        print("Please enter a float. " + specifiedRestriction)

        while not(allIsFine):
            errorMessage = ""
            CmdInput = str(input())
            try:
                answer = float(CmdInput)
                if hasAMin | hasAMax:
                    tooSmall = answer <= min if strict == True else answer < min
                    tooBig = answer >= max if strict == True else answer > max
                    if hasAMin & hasAMax:
                        if tooSmall | tooBig:
                            errorMessage = specifiedRestriction
                    elif hasAMin:
                        if tooSmall:
                            errorMessage = specifiedRestriction
                    elif tooBig:
                        errorMessage = specifiedRestriction
            except:
                errorMessage = "Your float is not valid."
            
            allIsFine = len(errorMessage) == 0

            if not(allIsFine):
                errorMessage += " Please retry: "
                print(errorMessage)

        return answer