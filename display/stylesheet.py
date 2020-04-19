


class gui_style(object):

    def progBarStyleCold():
        #TODO  Try and add the other base styling in normal format
        COLD_STYLE = """
            QProgressBar::chunk{
            background-color: #63a1f2;
            width: 22px;
            } 
            
            border: 1px solid black;
            border-radius: 5px;
            text-align: center;
            """
        return COLD_STYLE

    def progBarStyleNormal():
        #TODO  Try and add the other base styling in normal format
        NORMAL_STYLE = """
            QProgressBar::chunk{
            background-color: #63f280;
            width: 22px;
            } 
            
            border: 1px solid black;
            border-radius: 5px;
            text-align: center;
            """
        return NORMAL_STYLE

    def progBarStyleHot():
        #TODO  Try and add the other base styling in normal format
        HOT_STYLE = """
            QProgressBar::chunk{
            background-color: #f04f57;
            width: 22px;
            } 
            
            border: 1px solid black;
            border-radius: 5px;
            text-align: center;
            """
        return HOT_STYLE

    def btnStyleEnabled():
        ENABLED_STYLE = """
            background-color: #34eb4f;\n
            margin: 1px;\n
            border-color: #343536;\n
            border-style: outset;\n
            border-width: 1px;\n
            border-radius: 15px;\n
            """
        return ENABLED_STYLE

    def btnStyleDisabled():
        DISABLED_STYLE = """
            background-color: #fa5448;\n
            margin: 1px;\n
            border-color: #343536;\n
            border-style: outset;\n
            border-width: 1px;\n
            border-radius: 15px;\n
            """
        return DISABLED_STYLE

    def lblStyleConnected():
        CONNETED_STYLE = """
            background-color: #34eb4f;\n
            margin: 1px;\n
            border-color: #343536;\n
            border-style: outset;\n
            border-width: 1px;\n
            border-radius: 15px;\n
            font: 750 12pt “Arial Black”;\n
            """
        return CONNETED_STYLE

    def lblStyleDisconnected():
        DISCONNECTED_STYLE = """
            background-color: #fa5448;\n
            margin: 1px;\n
            border-color: #343536;\n
            border-style: outset;\n\n
            border-width: 1px;\n
            border-radius: 15px;\n
            font: 750 12pt “Arial Black”;\n
            """
        return DISCONNECTED_STYLE

