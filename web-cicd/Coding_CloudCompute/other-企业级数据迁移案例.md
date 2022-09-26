## 企业级数据迁移案例

Author: bavdu

Email: bavduer@163.om

---

- 逻辑卷的创建
- 数据的迁移

---

⚠️环境准备: `CentOS 7.5  x2`

#### 逻辑卷的创建

```shell
//查看到有一个空的磁盘为sdb
[root@JX01 ~]# lsblk
NAME            MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
sda               8:0    0   20G  0 disk
├─sda1            8:1    0    1G  0 part /boot
└─sda2            8:2    0   19G  0 part
  ├─centos-root 253:0    0   17G  0 lvm  /
  └─centos-swap 253:1    0    2G  0 lvm  [SWAP]
sdb               8:16   0   20G  0 disk
sr0              11:0    1  906M  0 rom
[root@JX01 ~]#

[root@JX01 ~]# fdisk /dev/sdb
命令(输入 m 获取帮助)：n
Partition type:
   p   primary (1 primary, 0 extended, 3 free)
   e   extended
Select (default p): p
分区号 (1-4，默认 1)：
起始 扇区 (2048-41943039，默认为 2048)：
将使用默认值 31459328
Last 扇区, +扇区 or +size{K,M,G} (31459328-41943039，默认为 41943039)：+14G
分区 2 已设置为 Linux 类型，大小设为 14 GiB

命令(输入 m 获取帮助)：w
The partition table has been altered!

Calling ioctl() to re-read partition table.

WARNING: Re-reading the partition table failed with error 16: 设备或资源忙.
The kernel still uses the old table. The new table will be used at
the next reboot or after you run partprobe(8) or kpartx(8)
正在同步磁盘。


//创建逻辑卷
[root@JX01 ~]# pvcreate /dev/sdb
  Physical volume "/dev/sdb" successfully created.
[root@JX01 ~]# vgcreate vgtest01 /dev/sdb
  Volume group "vgtest01" successfully created
[root@JX01 ~]# lvcreate -L 15G -n lvtest01 vgtest01
  Logical volume "lvtest01" created.
[root@JX01 ~]#

//查看创建出来的逻辑卷
[root@JX01 ~]# partprobe /dev/sdb
[root@JX01 ~]# lsblk
NAME                MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
sda                   8:0    0   20G  0 disk
├─sda1                8:1    0    1G  0 part /boot
└─sda2                8:2    0   19G  0 part
  ├─centos-root     253:0    0   17G  0 lvm  /
  └─centos-swap     253:1    0    2G  0 lvm  [SWAP]
sdb                   8:16   0   20G  0 disk
└─vgtest01-lvtest01 253:2    0   15G  0 lvm
sr0                  11:0    1  906M  0 rom
[root@JX01 ~]#

//格式化文件系统
[root@JX01 ~]# mkfs.ext4 /dev/vgtest01/lvtest01
mke2fs 1.42.9 (28-Dec-2013)
文件系统标签=
OS type: Linux
块大小=4096 (log=2)
分块大小=4096 (log=2)
Stride=0 blocks, Stripe width=0 blocks
983040 inodes, 3932160 blocks
196608 blocks (5.00%) reserved for the super user
第一个数据块=0
Maximum filesystem blocks=2151677952
120 block groups
32768 blocks per group, 32768 fragments per group
8192 inodes per group
Superblock backups stored on blocks:
	32768, 98304, 163840, 229376, 294912, 819200, 884736, 1605632, 2654208

Allocating group tables: 完成
正在写入inode表: 完成
Creating journal (32768 blocks): 完成
Writing superblocks and filesystem accounting information: 完成
[root@JX01 ~]#

//挂载逻辑卷到系统中
[root@JX01 ~]# vim /etc/fstab

/dev/vgtest01/lvtest01  /mnt    ext4    defaults        0 0

# /etc/fstab
# Created by anaconda on Thu Aug  2 02:21:19 2018
#
# Accessible filesystems, by reference, are maintained under '/dev/disk'
# See man pages fstab(5), findfs(8), mount(8) and/or blkid(8) for more info
#

[root@JX01 ~]# mount -a
[root@JX01 ~]# df -Th
文件系统                      类型      容量  已用  可用 已用% 挂载点
/dev/mapper/centos-root       xfs        17G  977M   17G    6% /
devtmpfs                      devtmpfs  476M     0  476M    0% /dev
tmpfs                         tmpfs     488M     0  488M    0% /dev/shm
tmpfs                         tmpfs     488M  7.7M  480M    2% /run
tmpfs                         tmpfs     488M     0  488M    0% /sys/fs/cgroup
/dev/sda1                     xfs      1014M  130M  885M   13% /boot
tmpfs                         tmpfs      98M     0   98M    0% /run/user/0
/dev/mapper/vgtest01-lvtest01 ext4       15G   41M   14G    1% /mnt
[root@JX01 ~]#

//把/etc、/var、/usr下的文件全部拷贝到lvtest01中
[root@JX01 ~]# cp -rf /etc/* /var/* /usr/* /mnt/

//开始进行数据的迁移,从JX01迁移到JX02中
[root@JX01 ~]# umount /mnt/
[root@JX01 ~]# vgrename vgtest01 newvgtest01
  Volume group "vgtest01" successfully renamed to "newvgtest01"
[root@JX01 ~]# lvrename /dev/newvgtest01/lvtest01 newlvtest01
  Renamed "lvtest01" to "newlvtest01" in volume group "newvgtest01"
[root@JX01 ~]#


//设置逻辑卷为非活动状态,即逻辑卷现在不可用
[root@JX01 ~]# vgchange -a n newvgtest01
  0 logical volume(s) in volume group "newvgtest01" now active
[root@JX01 ~]# lvdisplay
  --- Logical volume ---
  LV Path                /dev/newvgtest01/newlvtest01
  LV Name                newlvtest01
  VG Name                newvgtest01
  LV UUID                JvciWm-8CQQ-c8rg-OxDG-4Ex0-hifR-cZJe2E
  LV Write Access        read/write
  LV Creation host, time JX01, 2018-08-02 04:44:46 +0800
  LV Status              <NOT available>
  LV Size                15.00 GiB
  Current LE             3840
  Segments               1
  Allocation             inherit
  Read ahead sectors     auto
[root@JX01 ~]#

//导出逻辑卷,并查看状态
[root@JX01 ~]# vgexport newvgtest01
  Volume group "newvgtest01" successfully exported
[root@JX01 ~]# pvscan
  PV /dev/sda2   VG centos          lvm2 [<19.00 GiB / 0    free]
  PV /dev/sdb     is in exported VG newvgtest01 [<20.00 GiB / <5.00 GiB free]
  Total: 2 [38.99 GiB] / in use: 2 [38.99 GiB] / in no VG: 0 [0   ]
[root@JX01 ~]# pvdisplay
  Physical volume "/dev/sdb" of volume group "newvgtest01" is exported
  --- Physical volume ---
  PV Name               /dev/sdb
  VG Name               newvgtest01 (exported)
  PV Size               20.00 GiB / not usable 4.00 MiB
  Allocatable           yes
  PE Size               4.00 MiB
  Total PE              5119
  Free PE               1279
  Allocated PE          3840
  PV UUID               MWcBWi-pml0-gdDi-3bp6-l3oq-S3Qs-RSQiap
[root@JX01 ~]#


目标设备操作：
-1、扫描发现磁盘
[root@JX02 ~]# echo '- - - ' > /sys/class/scsi_host/host2/scan
[root@JX02 ~]# lsblk
NAME            MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
sda               8:0    0   20G  0 disk
├─sda1            8:1    0    1G  0 part /boot
└─sda2            8:2    0   19G  0 part
  ├─centos-root 253:0    0   17G  0 lvm  /
  └─centos-swap 253:1    0    2G  0 lvm  [SWAP]
sdb               8:16   0   20G  0 disk
└─sdb1            8:17   0    5G  0 part
  └─newvgtest01-newlvtest01 253:2    0    2G  0 lvm  /mnt
sr0              11:0    1  906M  0 rom
[root@JX02 ~]#

-2、扫描物理卷，然后导入卷组
[root@JX02 ~]# pvscan
  PV /dev/sda2   VG centos          lvm2 [<19.00 GiB / 0    free]
  PV /dev/sdb1   VG vgold           lvm2 [<5.00 GiB / <3.00 GiB free]
  Total: 2 [23.99 GiB] / in use: 2 [23.99 GiB] / in no VG: 0 [0   ]
[root@JX02 ~]#
[root@JX02 ~]# vgimport newvgtest01 
  Volume group "newvgtes01" successfully imported 
[root@JX02 ~]# vgdisplay newvgtest01

-3、激活逻辑卷
[root@CentOS7 ~]# vgchange  -a y newvgtest01  
  1 logical volume(s) in volume group "newvgtest01" now active 
[root@CentOS7 ~]# lvdisplay  
```

