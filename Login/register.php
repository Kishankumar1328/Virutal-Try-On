<?php
$conn = mysqli_connect("localhost", "root", "", "haitatsu");
if($conn === false){
	die("ERROR: Could not connect. "
	. mysqli_connect_error());
}
$nameuser = $_REQUEST['a'];
$username = $_REQUEST['b'];
$email = $_REQUEST['c'];
$passcode = $_REQUEST['d'];
$dob = $_REQUEST['e'];
$sql = "INSERT INTO users VALUES ('$nameuser','$username','$email','$passcode','$dob')";
	if(mysqli_query($conn, $sql)){
		header("Location:index.html");
	} else{
		echo "ERROR: Hush! Sorry $sql. "
			. mysqli_error($conn);
	}
mysqli_close($conn);
?>