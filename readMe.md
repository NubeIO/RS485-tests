dd if=/dev/zero of=large_file.testFile bs=1M count=1024

scp -P 2022 large_file.testFile rc@192.168.15.201:/home/rc/