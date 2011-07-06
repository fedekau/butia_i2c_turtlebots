//Autogenerated file using USB4ALL Descriptor generator V1.0  Author: Rafael Fernandez

#ifndef USBDSC_H
#define USBDSC_H
// I N C L U D E S ************************************************
#include "system\typedefs.h"
#include "autofiles\usbcfg.h" 
#include "system\usb\usb.h" 

//D E F I N I T I O N S ******************************************
#define MAX_NUM_INT             1 // For tracking Alternate Setting
#define EP0_BUFF_SIZE           8   // 8, 16, 32, or 64
#define CFG01 rom struct 	\
{   USB_CFG_DSC             cd01;	\
    USB_INTF_DSC            i00a00;	\
    USB_EP_DSC              ep01o_i00a00;	\
    USB_EP_DSC              ep01i_i00a00;	\
    USB_EP_DSC              ep02o_i00a00;	\
    USB_EP_DSC              ep02i_i00a00;	\
    USB_EP_DSC              ep03o_i00a00;	\
    USB_EP_DSC              ep03i_i00a00;	\
} cfg01
//		 E X T E R N S **************************************************
extern rom USB_DEV_DSC device_dsc;
extern CFG01;
extern rom const unsigned char *rom USB_CD_Ptr[];
extern rom const unsigned char *rom USB_SD_Ptr[];
#endif //USBDSC_H