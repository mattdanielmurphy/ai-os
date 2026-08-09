on open location this_URL
	if this_URL starts with "http://127.0.0.1:8643" or this_URL starts with "http://localhost:8643" then
		do shell script "curl -s '" & this_URL & "' > /dev/null 2>&1 &"
	else
		do shell script "open -a 'Google Chrome' '" & this_URL & "'"
	end if
end open location
