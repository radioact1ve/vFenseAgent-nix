If Wscript.Arguments.Count > 0 Then
    filepath = Wscript.Arguments.Item(0)

    Set FSObj = CreateObject("Scripting.FileSystemObject")
    Set file = FSObj.CreateTextFile(filepath, True)

Else
    Wscript.Echo "Please provide a text file to write to as argument."
    Wscript.Quit
End If

Set updateSession = CreateObject("Microsoft.Update.Session")
Set updateSearcher = updateSession.CreateUpdateSearcher()
Set searchResult = updateSearcher.Search("IsInstalled=0 and Type='Software' and IsHidden=0")

If searchResult.Updates.Count = 0 Then
    WScript.Echo "No updates found."
    WScript.Quit
End If

For I = 0 To searchResult.Updates.Count-1
    Set update = searchResult.Updates.Item(I)
        If InStr(update.Title, "Language Pack") Then
        Else
            file.Write "{" & VbCr
            file.Write "    ""name"": " & """" & update.Title & """" & "," & VbCr
            file.Write "    ""vendor_name"": " & """" & "Microsoft" & """" & "," & VbCr
            file.Write "    ""vendor_id"": " & """""" & "," & VbCr
            file.Write "    ""description"": " & """" & update.Description & """" & "," & VbCr

            If update.MoreInfoUrls.Count <= 0 Then
                file.Write "    ""support_url"": " & """" & "," & VbCr
            Else
                file.Write "    ""support_url"": " & """" & update.MoreInfoUrls.Item(0) & """" & "," & VbCr
            End If

            file.Write "    ""vendor_severity"": " & """" & update.MsrcSeverity & """" & "," & VbCr
            file.Write "    ""kb"": " & """""" & "," & VbCr

            file.Write "    ""file_data"": {" & VbCr
            For Each bundle In update.BundledUpdates
                file.Write "        [" & VbCr

                For Each udc In bundle.DownloadContents
                    file.Write "        ""file_hash"": " & """add later!""" & "," & VbCr
                    file.Write "        ""file_name"": " & """add later!""" & "," & VbCr

                    If IsNull(udc.DownloadUrl) Then
                    Else
                        file.Write "        ""file_uri"": " & """" & udc.DownloadUrl & """" &  "," & VbCr
                    End If

                    file.Write "        ]," & VbCr
                Next

            Next

            file.Write "    }," & VbCr
            file.Write "}," & VbCr

        End If
Next

file.Close
