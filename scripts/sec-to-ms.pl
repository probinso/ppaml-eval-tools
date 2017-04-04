#!/usr/bin/perl
use strict;
use warnings;
use File::Copy;
     
my $file = $ARGV[0] or die "Need to get CSV file on the command line\n";
my $outfile = $ARGV[0] . ".new";
my $timecol = $ARGV[1] or die "Second parameter is 1-based column of time\n";
my $header = 1;
     
open(my $data, '<', $file) or die "Could not open '$file' $!\n";
open(my $out, '>', $outfile) or die "Could not open '$outfile' $!\n";
     
while (my $line = <$data>)
{
	if ($header == 1)
	{
		print $out "$line";
		$header = 0;
	}
	else
	{
		my @fields;
		my $spaced = 0;
		if ($line =~ / /)
		{
			$spaced = 1;
		}
		chomp $line;

		if ($spaced == 1)
		{
			@fields = split ", " , $line;
		}
		else
		{
			@fields = split "," , $line;
		}

		for (my $col = 0; $col < @fields; $col++)
		{
			my $reprint = $fields[$col];
			if ($col == ($timecol-1))
			{
				$reprint = $fields[$col] * 1000;
			}
			print $out "$reprint";
			if ($col == (@fields - 1))
			{
				print $out "\n";
			}
			else
			{
				if ($spaced == 1)
				{
					print $out ", ";
				}
				else
				{
					print $out ",";
				}
			}
		}
	}
}

close($data);
close($out);

move($outfile, $file) or die "Unable to move .new to original!";
